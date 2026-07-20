"""
Etapa 3, secao 3.9 — os testes que tentam furar autenticacao e
permissao, nao so o caminho feliz. Mesma logica do teste dos dois
tenants na Etapa 2: o que prova a regra e a tentativa de furá-la.

O ultimo caso da secao 3.9 ("dono da Barbearia A nao gerencia usuarios
da B") depende de uma rota de recurso protegida que ainda nao existe
-- so nasce com a modelagem e o CRUD (Etapas 4 e 6). Quando essas
rotas existirem, esse caso entra na mesma suite dos dois tenants
(Etapa 2, secao 2.9). Aqui cobrimos tudo que ja e testavel com so
login e permissao de papel.
"""

from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest
from fastapi import HTTPException

from app.auth.dependencies import UsuarioAtual, exigir_papel
from app.config import get_settings
from app.modelos.usuario import Papel
from tests.conftest import criar_tenant, criar_usuario


def test_login_com_senha_certa_emite_token(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@barbearia-a.com")

    resposta = client.post(
        "/auth/login", json={"email": "dono@barbearia-a.com", "senha": "senha-correta"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]


def test_login_com_senha_errada_nega(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@barbearia-a.com")

    resposta = client.post(
        "/auth/login", json={"email": "dono@barbearia-a.com", "senha": "senha-errada"}
    )

    assert resposta.status_code == 401


def test_login_com_email_inexistente_nega(client, session):
    resposta = client.post("/auth/login", json={"email": "ninguem@nada.com", "senha": "x"})

    assert resposta.status_code == 401


def test_requisicao_sem_token_da_401(client):
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401


def test_token_adulterado_da_401(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@barbearia-a.com")

    token = client.post(
        "/auth/login", json={"email": "dono@barbearia-a.com", "senha": "senha-correta"}
    ).json()["access_token"]
    token_adulterado = token[:-1] + ("a" if token[-1] != "a" else "b")

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token_adulterado}"})

    assert resposta.status_code == 401


def test_token_expirado_da_401(client, session):
    tenant = criar_tenant(session)
    usuario = criar_usuario(session, tenant.id, "dono@barbearia-a.com")

    settings = get_settings()
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario.id),
        "tenant_id": usuario.tenant_id,
        "role": usuario.papel.value,
        "iat": agora - timedelta(hours=9),
        "exp": agora - timedelta(hours=1),
    }
    token_expirado = pyjwt.encode(payload, settings.secret_key, algorithm="HS256")

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token_expirado}"})

    assert resposta.status_code == 401


def test_me_devolve_tenant_e_papel_do_token(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@barbearia-a.com", papel=Papel.DONO)

    token = client.post(
        "/auth/login", json={"email": "dono@barbearia-a.com", "senha": "senha-correta"}
    ).json()["access_token"]

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["tenant_id"] == tenant.id
    assert corpo["papel"] == "dono"


def test_tenant_id_no_corpo_ou_url_e_ignorado(client, session):
    """
    Secao 3.4: nada que o cliente manda no corpo ou na URL pode
    influenciar tenant ou permissao. Um tenant_id de outro negocio na
    query string nao muda de quem e o token.
    """
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com")

    token = client.post(
        "/auth/login", json={"email": "dono@a.com", "senha": "senha-correta"}
    ).json()["access_token"]

    resposta = client.get(
        f"/auth/me?tenant_id={tenant_b.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["tenant_id"] == tenant_a.id


def test_atendente_nao_passa_por_exigir_papel_dono():
    verificador = exigir_papel(Papel.DONO)
    atendente = UsuarioAtual(id=1, tenant_id=1, papel=Papel.ATENDENTE.value)

    with pytest.raises(HTTPException) as excinfo:
        verificador(atendente)

    assert excinfo.value.status_code == 403


def test_dono_passa_por_exigir_papel_dono():
    verificador = exigir_papel(Papel.DONO)
    dono = UsuarioAtual(id=1, tenant_id=1, papel=Papel.DONO.value)

    assert verificador(dono) is dono
