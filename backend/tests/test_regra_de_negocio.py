"""
Etapa 5, secao 5.9 — a checagem de conflito e a transicao de status,
testadas direto na camada de servico (secao 5.8), sem subir a API.

O teste de race condition de verdade (duas criacoes simultaneas, so
uma vence) precisa da EXCLUDE constraint do Postgres (secao 5.6) —
SQLite nao tem GiST/btree_gist. Ele mora em test_race_condition.py,
separado, e so roda contra um Postgres de verdade.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.modelos.agendamento import StatusAgendamento
from app.servicos.agendamentos import criar_agendamento, mudar_status
from app.servicos.erros import (
    ConflitoDeHorarioError,
    ReferenciaDeOutroTenantError,
    TransicaoDeStatusInvalidaError,
)
from tests.conftest import criar_cliente, criar_servico, criar_tenant, criar_usuario


def _horario(hora: int, minuto: int = 0):
    return datetime(2026, 8, 1, hora, minuto, tzinfo=timezone.utc)


# ---------------------------------------------------------------------
# Conflito de horario (secao 5.2-5.5)
# ---------------------------------------------------------------------


def test_dois_agendamentos_em_horarios_distintos_sao_aceitos(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)

    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14), _horario(14, 30))
    segundo = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(15), _horario(15, 30)
    )

    assert segundo.id is not None


def test_novo_que_sobrepoe_o_fim_de_um_existente_e_rejeitado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15))

    with pytest.raises(ConflitoDeHorarioError):
        criar_agendamento(
            session, tenant.id, cliente.id, servico.id, _horario(14, 30), _horario(15, 30)
        )


def test_novo_que_sobrepoe_o_inicio_de_um_existente_e_rejeitado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15))

    with pytest.raises(ConflitoDeHorarioError):
        criar_agendamento(
            session, tenant.id, cliente.id, servico.id, _horario(13, 30), _horario(14, 30)
        )


def test_novo_contido_dentro_de_um_existente_e_rejeitado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14), _horario(16))

    with pytest.raises(ConflitoDeHorarioError):
        criar_agendamento(
            session, tenant.id, cliente.id, servico.id, _horario(14, 30), _horario(15, 30)
        )


def test_novo_que_contem_um_existente_e_rejeitado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14, 30), _horario(15))

    with pytest.raises(ConflitoDeHorarioError):
        criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14), _horario(16))


def test_novo_que_encosta_na_borda_e_aceito(session):
    """Secao 5.3: encostar nao e sobrepor (<=, >=, nao <, >)."""
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15))

    # comeca exatamente quando o outro termina
    seguinte = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(15), _horario(16)
    )
    assert seguinte.id is not None


def test_conflito_so_e_checado_dentro_do_mesmo_tenant(session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    cliente_a = criar_cliente(session, tenant_a.id)
    servico_a = criar_servico(session, tenant_a.id)
    cliente_b = criar_cliente(session, tenant_b.id)
    servico_b = criar_servico(session, tenant_b.id)

    criar_agendamento(session, tenant_a.id, cliente_a.id, servico_a.id, _horario(14), _horario(15))

    # mesmo horario, tenant diferente -> sem conflito
    agendamento_b = criar_agendamento(
        session, tenant_b.id, cliente_b.id, servico_b.id, _horario(14), _horario(15)
    )
    assert agendamento_b.id is not None


def test_horario_de_agendamento_cancelado_pode_ser_reusado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    original = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15)
    )

    mudar_status(session, tenant.id, original.id, StatusAgendamento.CANCELADO)

    reusado = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15)
    )
    assert reusado.id is not None


def test_criar_agendamento_rejeita_cliente_de_outro_tenant(session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    cliente_de_b = criar_cliente(session, tenant_b.id)
    servico_a = criar_servico(session, tenant_a.id)

    with pytest.raises(ReferenciaDeOutroTenantError):
        criar_agendamento(
            session, tenant_a.id, cliente_de_b.id, servico_a.id, _horario(14), _horario(15)
        )


# ---------------------------------------------------------------------
# Transicao de status (secao 5.7)
# ---------------------------------------------------------------------


def test_marcado_para_concluido_e_aceito(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    agendamento = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15)
    )

    atualizado = mudar_status(session, tenant.id, agendamento.id, StatusAgendamento.CONCLUIDO)
    assert atualizado.status == StatusAgendamento.CONCLUIDO.value


def test_marcado_para_cancelado_e_aceito(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    agendamento = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15)
    )

    atualizado = mudar_status(session, tenant.id, agendamento.id, StatusAgendamento.CANCELADO)
    assert atualizado.status == StatusAgendamento.CANCELADO.value


def test_concluido_para_marcado_e_rejeitado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    agendamento = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15)
    )
    mudar_status(session, tenant.id, agendamento.id, StatusAgendamento.CONCLUIDO)

    with pytest.raises(TransicaoDeStatusInvalidaError):
        mudar_status(session, tenant.id, agendamento.id, StatusAgendamento.MARCADO)


def test_cancelado_para_concluido_e_rejeitado(session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    agendamento = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(14), _horario(15)
    )
    mudar_status(session, tenant.id, agendamento.id, StatusAgendamento.CANCELADO)

    with pytest.raises(TransicaoDeStatusInvalidaError):
        mudar_status(session, tenant.id, agendamento.id, StatusAgendamento.CONCLUIDO)
