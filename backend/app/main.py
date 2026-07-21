"""
Ponto de entrada da API (Etapa 1, secao 1.6).

Responsabilidade unica deste arquivo: subir a instancia do FastAPI e
registrar os routers (os arquivos de app/rotas/) conforme eles vao
existindo. auth.py e o primeiro (Etapa 3); agendamentos.py chega com
a Etapa 5; clientes.py e servicos.py chegam com o CRUD de producao
da Etapa 6.
"""

from fastapi import FastAPI

from app.rotas import agendamentos, auth, clientes, servicos

app = FastAPI(
    title="Projeto Agenda - SaaS de Agendamento Multi-tenant",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(agendamentos.router)


@app.get("/health")
def health_check() -> dict:
    """
    Endpoint minimo de verificacao de vida da API.
    Nao pertence a nenhum tenant (nao tem tenant_id) porque nao
    acessa dado de negocio nenhum — so confirma que o processo esta de pe.
    """
    return {"status": "ok"}


# Proximo router: tenants.py (cadastro de negocio), quando a rota de
# criacao de tenant for escrita.
