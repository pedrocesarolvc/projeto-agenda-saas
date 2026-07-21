"""
Etapa 5, secao 5.5-5.6 e 5.9 — "o teste que impressiona": duas
criacoes concorrentes do mesmo horario, e so uma vence.

Isto exige um Postgres de verdade: a defesa robusta e a EXCLUDE
constraint (secao 5.6), que usa GiST/btree_gist -- recursos que nao
existem em SQLite (usado no resto da suite por conveniencia, Etapa 1,
secao 1.5). Sem Postgres real, este teste so provaria a verificacao
em codigo, que e justamente a parte fraca (secao 5.5) -- provaria
menos do que promete.

Por isso o modulo inteiro e pulado, com o motivo explicito, quando
POSTGRES_TEST_URL nao esta definida -- a mesma disciplina da secao
5.6 e da 5.9 (o teste que documenta a limitacao da 5.6): declarar,
nao esconder.

Para rodar localmente:
    docker run -d --name agenda-postgres-teste \
        -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=projeto_agenda \
        -p 55432:5432 postgres:16-alpine

    DATABASE_URL=postgresql://postgres:postgres@localhost:55432/projeto_agenda \
        alembic upgrade head

    POSTGRES_TEST_URL=postgresql://postgres:postgres@localhost:55432/projeto_agenda \
        pytest tests/test_race_condition.py -v
"""

import os
import threading
from datetime import datetime, timezone

import pytest
from sqlmodel import Session, create_engine, select

from app.modelos.agendamento import Agendamento
from app.modelos.cliente import Cliente
from app.modelos.servico import Servico
from app.modelos.tenant import Tenant
from app.servicos.agendamentos import _tem_conflito

POSTGRES_TEST_URL = os.getenv("POSTGRES_TEST_URL")

pytestmark = pytest.mark.skipif(
    POSTGRES_TEST_URL is None,
    reason=(
        "precisa de um Postgres de verdade para exercitar a EXCLUDE "
        "constraint da secao 5.6 (nao existe em SQLite); defina "
        "POSTGRES_TEST_URL com a migration ja aplicada para rodar"
    ),
)


def test_duas_criacoes_simultaneas_do_mesmo_horario_so_uma_vence():
    engine = create_engine(POSTGRES_TEST_URL)

    with Session(engine) as setup:
        tenant = Tenant(nome="Barbearia da corrida")
        setup.add(tenant)
        setup.commit()
        setup.refresh(tenant)

        cliente = Cliente(tenant_id=tenant.id, nome="Cliente da corrida")
        servico = Servico(tenant_id=tenant.id, nome="Corte", duracao_minutos=30, preco="40.00")
        setup.add(cliente)
        setup.add(servico)
        setup.commit()
        setup.refresh(cliente)
        setup.refresh(servico)

        tenant_id, cliente_id, servico_id = tenant.id, cliente.id, servico.id

    inicio = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)
    fim = datetime(2026, 9, 1, 10, 30, tzinfo=timezone.utc)

    barreira = threading.Barrier(2)
    resultados: list[tuple[str, object]] = []
    lock = threading.Lock()

    def tentar_marcar():
        # Sessao/conexao propria por thread -- e o que torna a
        # concorrencia real, nao duas chamadas sequenciais reusando a
        # mesma sessao.
        with Session(engine) as session:
            existe_conflito = _tem_conflito(session, tenant_id, inicio, fim)

            # So avanca para a insercao depois que AMBAS as threads ja
            # passaram pela verificacao -- forca de proposito a janela
            # verificar-inserir da secao 5.5, em vez de torcer para o
            # SO intercalar assim por acaso.
            barreira.wait()

            if existe_conflito:
                with lock:
                    resultados.append(("rejeitado_pela_verificacao_previa", None))
                return

            try:
                agendamento = Agendamento(
                    tenant_id=tenant_id,
                    cliente_id=cliente_id,
                    servico_id=servico_id,
                    inicio=inicio,
                    fim=fim,
                )
                session.add(agendamento)
                session.commit()
                with lock:
                    resultados.append(("aceito", agendamento.id))
            except Exception as erro:  # a EXCLUDE constraint reprova a 2a insercao
                session.rollback()
                with lock:
                    resultados.append(("rejeitado_pelo_banco", type(erro).__name__))

    threads = [threading.Thread(target=tentar_marcar) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    aceitos = [r for r in resultados if r[0] == "aceito"]
    rejeitados = [r for r in resultados if r[0] != "aceito"]

    # As duas passaram pela verificacao em codigo (a barreira garante
    # isso) -- se a defesa fosse so o codigo (secao 5.5, o furo), as
    # duas teriam inserido. O banco e quem impede a segunda de valer.
    assert len(aceitos) == 1, f"esperava exatamente 1 vencedor, veio {resultados}"
    assert len(rejeitados) == 1
    assert rejeitados[0][0] == "rejeitado_pelo_banco"

    with Session(engine) as verificacao:
        linhas = verificacao.exec(
            select(Agendamento).where(
                Agendamento.tenant_id == tenant_id,
                Agendamento.inicio == inicio,
            )
        ).all()
        assert len(linhas) == 1
