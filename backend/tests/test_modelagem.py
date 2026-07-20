"""
Etapa 4, secao 4.8 — o que se verifica numa modelagem e que a
estrutura sustenta as operacoes e a integridade, nao so que as
tabelas existem.
"""

import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.core.tenancy import pertence_ao_tenant
from app.modelos.agendamento import Agendamento
from app.modelos.cliente import Cliente
from app.modelos.servico import Servico
from app.modelos.usuario import Papel
from tests.conftest import criar_cliente, criar_servico, criar_tenant, criar_usuario

BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_criar_e_recuperar_cada_entidade_devolve_os_mesmos_dados(session):
    tenant = criar_tenant(session, nome="Barbearia A")
    usuario = criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id, nome="Fulano")
    servico = criar_servico(session, tenant.id, nome="Corte", duracao_minutos=30, preco="45.00")

    agendamento = Agendamento(
        tenant_id=tenant.id,
        cliente_id=cliente.id,
        servico_id=servico.id,
        inicio=datetime.now(timezone.utc),
        fim=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)

    # "Recuperar" de verdade: buscar de novo, nao so reusar o objeto
    # que acabou de ser criado.
    assert session.get(Cliente, cliente.id).nome == "Fulano"
    assert session.get(Servico, servico.id).nome == "Corte"
    agendamento_lido = session.get(Agendamento, agendamento.id)
    assert agendamento_lido.cliente_id == cliente.id
    assert agendamento_lido.servico_id == servico.id
    assert agendamento_lido.status == "marcado"  # default da secao 4.4
    assert usuario.tenant_id == tenant.id


def test_agendamento_liga_corretamente_a_cliente_e_servico(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id, nome="Ciclana")
    servico = criar_servico(session, tenant.id, nome="Barba")

    agendamento = Agendamento(
        tenant_id=tenant.id,
        cliente_id=cliente.id,
        servico_id=servico.id,
        inicio=datetime.now(timezone.utc),
        fim=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)

    # Via relacionamento (Relationship), nao so via id cru -- prova
    # que o desenho relacional da secao 4.3 funciona de verdade.
    assert agendamento.cliente.nome == "Ciclana"
    assert agendamento.servico.nome == "Barba"
    assert agendamento in cliente.agendamentos
    assert agendamento in servico.agendamentos


def test_fk_barra_cliente_id_inexistente(session):
    tenant = criar_tenant(session)
    servico = criar_servico(session, tenant.id)

    agendamento = Agendamento(
        tenant_id=tenant.id,
        cliente_id=999999,  # nao existe
        servico_id=servico.id,
        inicio=datetime.now(timezone.utc),
        fim=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    session.add(agendamento)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_agendamento_nao_deveria_aceitar_cliente_de_outro_tenant(session):
    """
    Secao 4.5: a FK garante que o cliente existe, nao que ele e do
    mesmo tenant do agendamento. pertence_ao_tenant() e a checagem
    que a camada de servico (Etapa 5) vai rodar antes de gravar --
    aqui provamos que ela distingue os dois casos corretamente.
    """
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    cliente_de_b = criar_cliente(session, tenant_b.id, nome="Cliente da B")

    assert pertence_ao_tenant(cliente_de_b, tenant_b.id) is True
    assert pertence_ao_tenant(cliente_de_b, tenant_a.id) is False


def test_inicio_e_fim_sobrevivem_ao_round_trip_em_utc(session):
    """
    Secao 4.4: DateTime(timezone=True) -> TIMESTAMPTZ no Postgres.
    SQLite (usado nos testes) nao preserva o offset de fuso no valor
    lido de volta -- devolve datetime "naive" -- entao a convencao da
    aplicacao e gravar e ler sempre em UTC (ver docstring de
    app/modelos/agendamento.py). O que este teste prova e que o
    INSTANTE sobrevive ao round-trip quando essa convencao e seguida.
    """
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)

    inicio = datetime(2026, 3, 10, 14, 0, tzinfo=timezone.utc)
    fim = inicio + timedelta(minutes=30)

    agendamento = Agendamento(
        tenant_id=tenant.id,
        cliente_id=cliente.id,
        servico_id=servico.id,
        inicio=inicio,
        fim=fim,
    )
    session.add(agendamento)
    session.commit()

    # Forca ida ao banco de novo, nao so devolver o objeto em cache
    # da identity map da sessao.
    session.expire_all()
    agendamento_lido = session.get(Agendamento, agendamento.id)

    assert agendamento_lido.inicio.replace(tzinfo=timezone.utc) == inicio
    assert agendamento_lido.fim.replace(tzinfo=timezone.utc) == fim


def test_migration_aplica_e_reverte_num_banco_limpo(tmp_path):
    db_path = tmp_path / "migracao_teste.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_path}"}

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    con = sqlite3.connect(db_path)
    tabelas = {linha[0] for linha in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert {"tenants", "usuarios", "clientes", "servicos", "agendamentos"} <= tabelas

    subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "base"],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    con = sqlite3.connect(db_path)
    tabelas = {linha[0] for linha in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert "tenants" not in tabelas
    assert "agendamentos" not in tabelas
