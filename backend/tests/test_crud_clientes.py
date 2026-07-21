"""
Etapa 6, secao 6.9 — CRUD de clientes: paginacao, busca, validacao,
update consciente, e o isolamento de tenant atravessando cada um.
"""

from app.modelos.usuario import Papel
from tests.conftest import autenticar, criar_cliente, criar_tenant, criar_usuario


def test_paginacao_devolve_o_tamanho_pedido_e_o_total_correto(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    for i in range(25):
        criar_cliente(session, tenant.id, nome=f"Cliente {i:02d}")
    headers = autenticar(client, "dono@a.com")

    pagina1 = client.get("/clientes?pagina=1&tamanho_pagina=20", headers=headers).json()
    pagina2 = client.get("/clientes?pagina=2&tamanho_pagina=20", headers=headers).json()

    assert pagina1["total"] == 25
    assert len(pagina1["itens"]) == 20
    assert len(pagina2["itens"]) == 5
    # Paginas nao se sobrepoem.
    ids_pagina1 = {item["id"] for item in pagina1["itens"]}
    ids_pagina2 = {item["id"] for item in pagina2["itens"]}
    assert ids_pagina1.isdisjoint(ids_pagina2)


def test_tamanho_pagina_acima_do_teto_e_limitado_nao_obedecido_cego(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/clientes?tamanho_pagina=999999", headers=headers)

    assert resposta.status_code == 422  # Pydantic barra via le=100 (secao 6.3)


def test_paginacao_respeita_o_tenant(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    criar_cliente(session, tenant_a.id, nome="Cliente de A")
    for i in range(5):
        criar_cliente(session, tenant_b.id, nome=f"Cliente de B {i}")
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/clientes", headers=headers).json()

    assert resposta["total"] == 1
    assert resposta["itens"][0]["nome"] == "Cliente de A"


def test_busca_por_nome_parcial_encontra(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    criar_cliente(session, tenant.id, nome="Joao Silva")
    criar_cliente(session, tenant.id, nome="Maria Souza")
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/clientes?busca=silva", headers=headers).json()

    assert resposta["total"] == 1
    assert resposta["itens"][0]["nome"] == "Joao Silva"


def test_busca_sem_correspondencia_devolve_vazio_nao_erro(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    criar_cliente(session, tenant.id, nome="Joao Silva")
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/clientes?busca=inexistente", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 0


def test_busca_nunca_traz_cliente_de_outro_tenant(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    criar_cliente(session, tenant_b.id, nome="Joao Silva")  # so existe na B
    headers = autenticar(client, "dono@a.com")

    resposta = client.get("/clientes?busca=silva", headers=headers).json()

    assert resposta["total"] == 0


def test_criar_cliente_com_dado_malformado_devolve_422(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    headers = autenticar(client, "dono@a.com")

    resposta = client.post("/clientes", headers=headers, json={"telefone": "sem nome"})

    assert resposta.status_code == 422


def test_update_parcial_altera_so_o_campo_enviado(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant.id, nome="Joao Silva")
    headers = autenticar(client, "dono@a.com")

    resposta = client.put(
        f"/clientes/{cliente.id}", headers=headers, json={"telefone": "11999999999"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome"] == "Joao Silva"  # preservado
    assert corpo["telefone"] == "11999999999"  # alterado


def test_update_nao_aceita_mudar_tenant_id(client, session):
    """
    Secao 6.6: tenant_id nunca se atualiza. ClienteAtualizar nem tem
    esse campo -- um tenant_id extra no corpo e simplesmente ignorado
    pelo Pydantic (schema fecha a porta antes de qualquer logica).
    """
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    cliente = criar_cliente(session, tenant_a.id, nome="Joao")
    headers = autenticar(client, "dono@a.com")

    resposta = client.put(
        f"/clientes/{cliente.id}",
        headers=headers,
        json={"nome": "Joao Atualizado", "tenant_id": tenant_b.id},
    )

    assert resposta.status_code == 200
    # O cliente continua no tenant A -- o campo extra foi ignorado.
    verificacao = client.get(f"/clientes/{cliente.id}", headers=headers)
    assert verificacao.status_code == 200


def test_obter_cliente_de_outro_tenant_devolve_404(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    cliente_de_b = criar_cliente(session, tenant_b.id)
    headers = autenticar(client, "dono@a.com")

    resposta = client.get(f"/clientes/{cliente_de_b.id}", headers=headers)

    assert resposta.status_code == 404


def test_remover_cliente_de_outro_tenant_devolve_404(client, session):
    tenant_a = criar_tenant(session, nome="Barbearia A")
    tenant_b = criar_tenant(session, nome="Barbearia B")
    criar_usuario(session, tenant_a.id, "dono@a.com", papel=Papel.DONO)
    cliente_de_b = criar_cliente(session, tenant_b.id)
    headers = autenticar(client, "dono@a.com")

    resposta = client.delete(f"/clientes/{cliente_de_b.id}", headers=headers)

    assert resposta.status_code == 404


def test_criar_listar_remover_cliente_fluxo_completo(client, session):
    tenant = criar_tenant(session)
    criar_usuario(session, tenant.id, "dono@a.com", papel=Papel.DONO)
    headers = autenticar(client, "dono@a.com")

    criado = client.post("/clientes", headers=headers, json={"nome": "Novo Cliente"}).json()
    assert client.get("/clientes", headers=headers).json()["total"] == 1

    remocao = client.delete(f"/clientes/{criado['id']}", headers=headers)
    assert remocao.status_code == 204
    assert client.get("/clientes", headers=headers).json()["total"] == 0
