"""
Etapa 6, secao 6.9 — agendamentos: listagem paginada com filtro
(status, dia) e busca (nome do cliente), e remarcar (update
consciente que re-checa conflito, secao 6.6).
"""

from datetime import datetime, timezone

from app.modelos.usuario import Papel
from app.servicos.agendamentos import criar_agendamento, mudar_status
from app.modelos.agendamento import StatusAgendamento
from tests.conftest import autenticar, criar_cliente, criar_servico, criar_tenant, criar_usuario


def _horario(dia: int, hora: int):
    return datetime(2026, 9, dia, hora, 0, tzinfo=timezone.utc)


def test_listagem_pagina_e_ordena_por_inicio(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    for hora in [16, 14, 15]:  # fora de ordem de proposito
        criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(1, hora), _horario(1, hora + 1))
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/agendamentos", headers=headers).json()

    assert resposta["total"] == 3
    horarios = [item["inicio"] for item in resposta["itens"]]
    assert horarios == sorted(horarios)  # ordenado por inicio, secao 6.3


def test_filtro_por_status_devolve_so_aquele_status(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    a1 = criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(1, 14), _horario(1, 15))
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(1, 16), _horario(1, 17))
    mudar_status(session, tenant.id, a1.id, StatusAgendamento.CANCELADO)
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/agendamentos?status_filtro=cancelado", headers=headers).json()

    assert resposta["total"] == 1
    assert resposta["itens"][0]["status"] == "cancelado"


def test_filtro_por_dia_combinado_com_status(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(1, 14), _horario(1, 15))
    criar_agendamento(session, tenant.id, cliente.id, servico.id, _horario(2, 14), _horario(2, 15))
    headers = autenticar(client, "dono@a.com")

    resposta = client.get(
        "/agendamentos?dia=2026-09-01&status_filtro=marcado", headers=headers
    ).json()

    assert resposta["total"] == 1
    assert resposta["itens"][0]["inicio"].startswith("2026-09-01")


def test_busca_por_nome_do_cliente_encontra(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente_silva = criar_cliente(session, tenant.id, nome="Joao Silva")
    cliente_souza = criar_cliente(session, tenant.id, nome="Maria Souza")
    servico = criar_servico(session, tenant.id)
    criar_agendamento(session, tenant.id, cliente_silva.id, servico.id, _horario(1, 14), _horario(1, 15))
    criar_agendamento(session, tenant.id, cliente_souza.id, servico.id, _horario(1, 16), _horario(1, 17))
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/agendamentos?cliente=silva", headers=headers).json()

    assert resposta["total"] == 1


def test_listagem_e_busca_nunca_trazem_dado_de_outro_tenant(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    cliente_b = criar_cliente(session, tenant_b.id, nome="Joao Silva")
    servico_b = criar_servico(session, tenant_b.id)
    criar_agendamento(session, tenant_b.id, cliente_b.id, servico_b.id, _horario(1, 14), _horario(1, 15))
    headers = autenticar(client, "dono@a.com")

    listagem = client.get("/agendamentos", headers=headers).json()
    busca = client.get("/agendamentos?cliente=silva", headers=headers).json()

    assert listagem["total"] == 0
    assert busca["total"] == 0


def test_remarcar_para_horario_livre_e_aceito(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    agendamento = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(1, 14), _horario(1, 15)
    )
    headers = autenticar(client, "dono@a.com")

    resposta = client.patch(
        f"/agendamentos/{agendamento.id}",
        headers=headers,
        json={"inicio": "2026-09-01T18:00:00+00:00", "fim": "2026-09-01T19:00:00+00:00"},
    )

    assert resposta.status_code == 200
    # SQLite perde o tzinfo na releitura (Etapa 4); o instante em UTC
    # e o que importa, nao a presenca literal do sufixo "Z".
    assert resposta.json()["inicio"].startswith("2026-09-01T18:00:00")


def test_remarcar_para_horario_ocupado_e_rejeitado_409(client, session):
    """Secao 6.6: remarcar re-checa conflito -- senao recria o
    problema que a Etapa 5 resolveu."""
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    ocupado = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(1, 14), _horario(1, 15)
    )
    a_remarcar = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(1, 16), _horario(1, 17)
    )
    headers = autenticar(client, "dono@a.com")

    resposta = client.patch(
        f"/agendamentos/{a_remarcar.id}",
        headers=headers,
        json={"inicio": "2026-09-01T14:30:00+00:00", "fim": "2026-09-01T15:30:00+00:00"},
    )

    assert resposta.status_code == 409
    assert ocupado.id  # so para deixar claro o que causou o 409


def test_remarcar_para_o_proprio_horario_e_aceito(client, session):
    """O agendamento nao deve 'conflitar consigo mesmo' (ignorar_id
    em _tem_conflito, secao 6.6)."""
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    agendamento = criar_agendamento(
        session, tenant.id, cliente.id, servico.id, _horario(1, 14), _horario(1, 15)
    )
    headers = autenticar(client, "dono@a.com")

    resposta = client.patch(
        f"/agendamentos/{agendamento.id}",
        headers=headers,
        json={"inicio": "2026-09-01T14:00:00+00:00", "fim": "2026-09-01T15:00:00+00:00"},
    )

    assert resposta.status_code == 200


def test_remarcar_agendamento_de_outro_tenant_devolve_404(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    cliente_b = criar_cliente(session, tenant_b.id)
    servico_b = criar_servico(session, tenant_b.id)
    agendamento_b = criar_agendamento(
        session, tenant_b.id, cliente_b.id, servico_b.id, _horario(1, 14), _horario(1, 15)
    )
    headers = autenticar(client, "dono@a.com")

    resposta = client.patch(
        f"/agendamentos/{agendamento_b.id}",
        headers=headers,
        json={"inicio": "2026-09-01T18:00:00+00:00", "fim": "2026-09-01T19:00:00+00:00"},
    )

    assert resposta.status_code == 404
