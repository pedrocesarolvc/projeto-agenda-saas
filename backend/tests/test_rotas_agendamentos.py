"""
Etapa 5 — as mesmas regras de negocio (ja testadas direto no servico
em test_regra_de_negocio.py), agora atravessando a rota HTTP de
verdade: autenticacao (Etapa 3) + tenancy (Etapa 2) + erro de
dominio virando status HTTP (secao 5.8).
"""

from datetime import datetime, timezone

from app.modelos.usuario import Papel
from tests.conftest import criar_cliente, criar_servico, criar_tenant, criar_usuario


def _autenticar(client, email: str) -> dict:
    token = client.post("/auth/login", json={"email": email, "senha": "senha-correta"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def test_criar_agendamento_via_rota_devolve_201(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    headers = _autenticar(client, "dono@a.com")

    resposta = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "cliente_id": cliente.id,
            "servico_id": servico.id,
            "inicio": "2026-08-01T14:00:00+00:00",
            "fim": "2026-08-01T14:30:00+00:00",
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "marcado"


def test_criar_agendamento_com_conflito_devolve_409(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    headers = _autenticar(client, "dono@a.com")

    payload = {
        "cliente_id": cliente.id,
        "servico_id": servico.id,
        "inicio": "2026-08-01T14:00:00+00:00",
        "fim": "2026-08-01T14:30:00+00:00",
    }
    client.post("/agendamentos", headers=headers, json=payload)
    resposta = client.post("/agendamentos", headers=headers, json=payload)

    assert resposta.status_code == 409


def test_criar_agendamento_sem_token_devolve_401(client, session):
    tenant = criar_tenant(session)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)

    resposta = client.post(
        "/agendamentos",
        json={
            "cliente_id": cliente.id,
            "servico_id": servico.id,
            "inicio": "2026-08-01T14:00:00+00:00",
            "fim": "2026-08-01T14:30:00+00:00",
        },
    )

    assert resposta.status_code == 401


def test_criar_agendamento_com_cliente_de_outro_tenant_devolve_404(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    cliente_de_b = criar_cliente(session, tenant_b.id)
    servico_a = criar_servico(session, tenant_a.id)
    headers = _autenticar(client, "dono@a.com")

    resposta = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "cliente_id": cliente_de_b.id,
            "servico_id": servico_a.id,
            "inicio": "2026-08-01T14:00:00+00:00",
            "fim": "2026-08-01T14:30:00+00:00",
        },
    )

    assert resposta.status_code == 404


def test_transicao_de_status_invalida_via_rota_devolve_409(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id)
    servico = criar_servico(session, tenant.id)
    headers = _autenticar(client, "dono@a.com")

    criado = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "cliente_id": cliente.id,
            "servico_id": servico.id,
            "inicio": "2026-08-01T14:00:00+00:00",
            "fim": "2026-08-01T14:30:00+00:00",
        },
    ).json()

    ok = client.patch(
        f"/agendamentos/{criado['id']}/status", headers=headers, json={"status": "concluido"}
    )
    assert ok.status_code == 200

    invalido = client.patch(
        f"/agendamentos/{criado['id']}/status", headers=headers, json={"status": "marcado"}
    )
    assert invalido.status_code == 409
