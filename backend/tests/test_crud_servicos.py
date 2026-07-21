"""
Etapa 6, secao 6.9 — CRUD de servicos: sempre pagina (mesmo "sem ter
muitos", secao 6.3), valida preco/duracao, e isola por tenant.
"""

from app.modelos.usuario import Papel
from tests.conftest import autenticar, criar_servico, criar_tenant, criar_usuario


def test_listagem_de_servicos_pagina_mesmo_com_poucos_registros(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    criar_servico(session, tenant.id, nome="Corte")
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/servicos", headers=headers).json()

    assert resposta["total"] == 1
    assert resposta["pagina"] == 1
    assert resposta["tamanho_pagina"] == 20


def test_listagem_de_servicos_respeita_o_tenant(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    criar_servico(session, tenant_b.id, nome="Corte da B")
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/servicos", headers=headers).json()

    assert resposta["total"] == 0


def test_criar_servico_com_preco_negativo_devolve_422(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    headers = autenticar(client, "dono@a.com")

    resposta = client.post(
        "/servicos",
        headers=headers,
        json={"nome": "Corte", "duracao_minutos": 30, "preco": "-10.00"},
    )

    assert resposta.status_code == 422


def test_criar_servico_com_duracao_zero_devolve_422(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    headers = autenticar(client, "dono@a.com")

    resposta = client.post(
        "/servicos",
        headers=headers,
        json={"nome": "Corte", "duracao_minutos": 0, "preco": "40.00"},
    )

    assert resposta.status_code == 422


def test_criar_servico_valido_devolve_201(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    headers = autenticar(client, "dono@a.com")

    resposta = client.post(
        "/servicos",
        headers=headers,
        json={"nome": "Corte", "duracao_minutos": 30, "preco": "40.00"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["preco"] == "40.00"


def test_update_parcial_de_servico_preserva_campos_nao_enviados(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    servico = criar_servico(session, tenant.id, nome="Corte", duracao_minutos=30, preco="40.00")
    headers = autenticar(client, "dono@a.com")

    resposta = client.put(f"/servicos/{servico.id}", headers=headers, json={"preco": "55.00"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome"] == "Corte"
    assert corpo["duracao_minutos"] == 30
    assert corpo["preco"] == "55.00"


def test_update_de_servico_com_preco_negativo_devolve_422(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    servico = criar_servico(session, tenant.id)
    headers = autenticar(client, "dono@a.com")

    resposta = client.put(f"/servicos/{servico.id}", headers=headers, json={"preco": "-1.00"})

    assert resposta.status_code == 422


def test_obter_servico_de_outro_tenant_devolve_404(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    servico_de_b = criar_servico(session, tenant_b.id)
    headers = autenticar(client, "dono@a.com")

    resposta = client.get(f"/servicos/{servico_de_b.id}", headers=headers)

    assert resposta.status_code == 404
