"""
Etapa 7, secao 7.5 — os tres testes que atravessam o sistema inteiro,
so pela API (nenhum atalho direto no banco). Sao o atestado do
projeto; o segundo (dois tenants) e o mais valioso do portfolio
inteiro -- a prova executavel de "eu sei fazer multi-tenancy sem
vazar dados".
"""


def _registrar(client, nome_negocio: str, email: str) -> dict:
    resposta = client.post(
        "/auth/registrar-negocio",
        json={
            "nome_negocio": nome_negocio,
            "nome_dono": "Dono",
            "email": email,
            "senha": "senha123",
        },
    )
    assert resposta.status_code == 201
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_fluxo_feliz_completo(client):
    """
    registrar -> logar -> cadastrar servico -> cadastrar cliente ->
    marcar agendamento -> ve-lo na agenda.
    """
    headers = _registrar(client, "Barbearia Fluxo Feliz", "fluxo@feliz.com")

    # logar (alem do token que o registro ja devolveu -- prova que a
    # senha cadastrada no registro funciona de verdade no login).
    login = client.post(
        "/auth/login", json={"email": "fluxo@feliz.com", "senha": "senha123"}
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    servico = client.post(
        "/servicos",
        headers=headers,
        json={"nome": "Corte", "duracao_minutos": 30, "preco": "40.00"},
    )
    assert servico.status_code == 201
    servico_id = servico.json()["id"]

    cliente = client.post("/clientes", headers=headers, json={"nome": "Fulano de Tal"})
    assert cliente.status_code == 201
    cliente_id = cliente.json()["id"]

    agendamento = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "inicio": "2026-10-05T14:00:00+00:00",
            "fim": "2026-10-05T14:30:00+00:00",
        },
    )
    assert agendamento.status_code == 201
    agendamento_id = agendamento.json()["id"]

    agenda = client.get("/agendamentos", headers=headers)
    assert agenda.status_code == 200
    ids_na_agenda = {item["id"] for item in agenda.json()["itens"]}
    assert agendamento_id in ids_na_agenda

    # Etapa 7, secao 7.3: a interface sempre sabe em qual negocio o
    # usuario esta.
    meu_negocio = client.get("/tenants/me", headers=headers)
    assert meu_negocio.status_code == 200
    assert meu_negocio.json()["nome"] == "Barbearia Fluxo Feliz"


def test_dois_tenants_um_nunca_alcanca_o_dado_do_outro_por_nenhuma_rota(client):
    """
    O atestado do portfolio: dois negocios completos (cada um com
    servico, cliente e agendamento proprios), e o tenant A tentando
    de toda forma possivel alcancar o dado do B -- listar, buscar,
    filtrar, ler por id, editar, remarcar, mudar status, remover.
    Todas tem que falhar.
    """
    headers_a = _registrar(client, "Barbearia A", "dono@a-e2e.com")
    headers_b = _registrar(client, "Barbearia B", "dono@b-e2e.com")

    servico_b = client.post(
        "/servicos",
        headers=headers_b,
        json={"nome": "Corte B", "duracao_minutos": 30, "preco": "40.00"},
    ).json()
    cliente_b = client.post(
        "/clientes", headers=headers_b, json={"nome": "Cliente Silva da B"}
    ).json()
    agendamento_b = client.post(
        "/agendamentos",
        headers=headers_b,
        json={
            "cliente_id": cliente_b["id"],
            "servico_id": servico_b["id"],
            "inicio": "2026-10-06T14:00:00+00:00",
            "fim": "2026-10-06T14:30:00+00:00",
        },
    ).json()

    # Listagens de A nunca trazem nada de B.
    assert client.get("/clientes", headers=headers_a).json()["total"] == 0
    assert client.get("/servicos", headers=headers_a).json()["total"] == 0
    assert client.get("/agendamentos", headers=headers_a).json()["total"] == 0

    # Busca por nome tambem nao vaza.
    busca = client.get("/clientes?busca=silva", headers=headers_a).json()
    assert busca["total"] == 0
    busca_agenda = client.get("/agendamentos?cliente=silva", headers=headers_a).json()
    assert busca_agenda["total"] == 0

    # Leitura direta por id -> 404, nao 200 nem 403 (Etapa 2, secao 2.5).
    assert client.get(f"/clientes/{cliente_b['id']}", headers=headers_a).status_code == 404
    assert client.get(f"/servicos/{servico_b['id']}", headers=headers_a).status_code == 404
    assert (
        client.get(f"/agendamentos/{agendamento_b['id']}", headers=headers_a).status_code == 404
    )

    # Escrita tambem barrada: update, remarcar, mudar status, remover.
    assert (
        client.put(
            f"/clientes/{cliente_b['id']}", headers=headers_a, json={"nome": "Roubado"}
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"/servicos/{servico_b['id']}", headers=headers_a, json={"preco": "1.00"}
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/agendamentos/{agendamento_b['id']}",
            headers=headers_a,
            json={"inicio": "2026-10-06T18:00:00+00:00", "fim": "2026-10-06T18:30:00+00:00"},
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/agendamentos/{agendamento_b['id']}/status",
            headers=headers_a,
            json={"status": "cancelado"},
        ).status_code
        == 404
    )
    assert client.delete(f"/clientes/{cliente_b['id']}", headers=headers_a).status_code == 404
    assert client.delete(f"/servicos/{servico_b['id']}", headers=headers_a).status_code == 404

    # E o dado de B continua intacto e visivel para B.
    assert client.get("/clientes", headers=headers_b).json()["total"] == 1
    assert client.get(f"/agendamentos/{agendamento_b['id']}", headers=headers_b).status_code == 200


def test_conflito_de_horario_ponta_a_ponta(client):
    """Marcar um horario, tentar marcar outro sobreposto, 409 -- a
    regra da Etapa 5 vista pela borda HTTP."""
    headers = _registrar(client, "Barbearia Conflito", "conflito@e2e.com")

    servico = client.post(
        "/servicos",
        headers=headers,
        json={"nome": "Corte", "duracao_minutos": 30, "preco": "40.00"},
    ).json()
    cliente = client.post("/clientes", headers=headers, json={"nome": "Fulano"}).json()

    primeiro = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "cliente_id": cliente["id"],
            "servico_id": servico["id"],
            "inicio": "2026-10-07T14:00:00+00:00",
            "fim": "2026-10-07T14:30:00+00:00",
        },
    )
    assert primeiro.status_code == 201

    sobreposto = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "cliente_id": cliente["id"],
            "servico_id": servico["id"],
            "inicio": "2026-10-07T14:15:00+00:00",
            "fim": "2026-10-07T14:45:00+00:00",
        },
    )
    assert sobreposto.status_code == 409
    assert "horario" in sobreposto.json()["detail"].lower()
