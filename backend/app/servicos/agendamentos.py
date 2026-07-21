"""
Camada de servico para agendamento (Etapa 5, secao 5.8): a rota
traduz HTTP, aqui e onde o dominio decide. Nada neste arquivo sabe
que FastAPI existe.

As duas regras da etapa:
  criar_agendamento  -> conflito de horario (secao 5.2-5.5)
  mudar_status       -> transicao de status (secao 5.7)
"""

from datetime import datetime

from sqlmodel import Session, select

from app.core.tenancy import pertence_ao_tenant
from app.modelos.agendamento import Agendamento, StatusAgendamento
from app.modelos.cliente import Cliente
from app.modelos.servico import Servico
from app.servicos.erros import (
    ConflitoDeHorarioError,
    ReferenciaDeOutroTenantError,
    TransicaoDeStatusInvalidaError,
)

# A maquina de estados da secao 5.7: de cada estado, para quais
# estados a transicao e permitida. Ausente do dicionario ou conjunto
# vazio = nenhuma saida (estado terminal).
_TRANSICOES_VALIDAS: dict[str, set[str]] = {
    StatusAgendamento.MARCADO.value: {
        StatusAgendamento.CONCLUIDO.value,
        StatusAgendamento.CANCELADO.value,
    },
    StatusAgendamento.CONCLUIDO.value: set(),
    StatusAgendamento.CANCELADO.value: set(),
}


def _tem_conflito(session: Session, tenant_id: int, inicio: datetime, fim: datetime) -> bool:
    """
    A query da secao 5.4, traduzida para SQLModel. status <> cancelado
    porque um agendamento cancelado libera o horario (secao 5.7 se
    encontra com a 5.4 aqui). tenant_id sempre, porque um conflito so
    existe dentro do mesmo negocio (Etapa 2).

    A condicao de sobreposicao e a negacao dos dois casos de
    nao-conflito (secao 5.3): nao conflita quando um termina antes do
    outro comecar ou comeca depois do outro terminar. Aqui, invertida,
    ela vira "inicio existente < fim novo E fim existente > inicio
    novo" -- <, > (nao <=, >=), porque encostar na borda nao e
    sobrepor.
    """
    query = (
        select(Agendamento)
        .where(Agendamento.tenant_id == tenant_id)
        .where(Agendamento.status != StatusAgendamento.CANCELADO.value)
        .where(Agendamento.inicio < fim)
        .where(Agendamento.fim > inicio)
    )
    return session.exec(query).first() is not None


def criar_agendamento(
    session: Session,
    tenant_id: int,
    cliente_id: int,
    servico_id: int,
    inicio: datetime,
    fim: datetime,
) -> Agendamento:
    """
    Verificacao em codigo (mensagem amigavel) + constraint no banco
    (garantia real sob concorrencia) — secao 5.6. Esta funcao cobre a
    primeira; a EXCLUDE constraint da migration cobre a segunda. Se
    duas chamadas concorrentes passarem as duas pela checagem em
    codigo (a race condition da secao 5.5), a segunda inserção ainda
    assim falha no banco.
    """
    cliente = session.get(Cliente, cliente_id)
    if not pertence_ao_tenant(cliente, tenant_id):
        raise ReferenciaDeOutroTenantError("cliente nao pertence a este tenant")

    servico = session.get(Servico, servico_id)
    if not pertence_ao_tenant(servico, tenant_id):
        raise ReferenciaDeOutroTenantError("servico nao pertence a este tenant")

    if _tem_conflito(session, tenant_id, inicio, fim):
        raise ConflitoDeHorarioError("este horario ja esta ocupado")

    agendamento = Agendamento(
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        servico_id=servico_id,
        inicio=inicio,
        fim=fim,
    )
    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)
    return agendamento


def mudar_status(
    session: Session,
    tenant_id: int,
    agendamento_id: int,
    novo_status: StatusAgendamento,
) -> Agendamento:
    agendamento = session.get(Agendamento, agendamento_id)
    if not pertence_ao_tenant(agendamento, tenant_id):
        raise ReferenciaDeOutroTenantError("agendamento nao pertence a este tenant")

    transicoes_permitidas = _TRANSICOES_VALIDAS.get(agendamento.status, set())
    if novo_status.value not in transicoes_permitidas:
        raise TransicaoDeStatusInvalidaError(
            f"nao e possivel ir de '{agendamento.status}' para '{novo_status.value}'"
        )

    agendamento.status = novo_status.value
    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)
    return agendamento
