"""
Etapa 7, secao 7.2 — POST /auth/registrar-negocio: cria tenant + dono,
devolve token direto (login automatico apos registro).
"""


def test_registrar_negocio_cria_tenant_e_dono_e_devolve_token(client):
    resposta = client.post(
        "/auth/registrar-negocio",
        json={
            "nome_negocio": "Barbearia Nova",
            "nome_dono": "Fulano",
            "email": "dono@nova.com",
            "senha": "senha123",
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]

    # O token ja funciona -- login automatico apos registro.
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {corpo['access_token']}"})
    assert me.status_code == 200
    assert me.json()["papel"] == "dono"


def test_registrar_negocio_com_email_ja_cadastrado_devolve_409(client):
    dados = {
        "nome_negocio": "Barbearia A",
        "nome_dono": "Fulano",
        "email": "duplicado@x.com",
        "senha": "senha123",
    }
    primeiro = client.post("/auth/registrar-negocio", json=dados)
    assert primeiro.status_code == 201

    segundo = client.post(
        "/auth/registrar-negocio",
        json={**dados, "nome_negocio": "Outra Barbearia"},
    )
    assert segundo.status_code == 409


def test_registrar_negocio_com_dado_malformado_devolve_422(client):
    resposta = client.post("/auth/registrar-negocio", json={"nome_negocio": "Sem o resto"})

    assert resposta.status_code == 422


def test_dois_donos_registrados_ficam_em_tenants_diferentes(client):
    """
    Cada registro cria seu proprio tenant -- dois donos que se
    registram nao caem sob o mesmo negocio por acaso.
    """
    r1 = client.post(
        "/auth/registrar-negocio",
        json={
            "nome_negocio": "Barbearia A",
            "nome_dono": "Dono A",
            "email": "a@x.com",
            "senha": "senha123",
        },
    ).json()
    r2 = client.post(
        "/auth/registrar-negocio",
        json={
            "nome_negocio": "Barbearia B",
            "nome_dono": "Dono B",
            "email": "b@x.com",
            "senha": "senha123",
        },
    ).json()

    tenant_a = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {r1['access_token']}"}
    ).json()["tenant_id"]
    tenant_b = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {r2['access_token']}"}
    ).json()["tenant_id"]

    assert tenant_a != tenant_b
