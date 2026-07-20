"""
Ponto de entrada da API (Etapa 1, secao 1.6).

Responsabilidade unica deste arquivo: subir a instancia do FastAPI e
registrar os routers (os arquivos de app/rotas/) conforme eles vao
existindo. auth.py e o primeiro (Etapa 3); os demais chegam com as
etapas de modelagem e regra de negocio.
"""

from fastapi import FastAPI

from app.rotas import auth

app = FastAPI(
    title="Projeto Agenda - SaaS de Agendamento Multi-tenant",
    version="0.1.0",
)

app.include_router(auth.router)


@app.get("/health")
def health_check() -> dict:
    """
    Endpoint minimo de verificacao de vida da API.
    Nao pertence a nenhum tenant (nao tem tenant_id) porque nao
    acessa dado de negocio nenhum — so confirma que o processo esta de pe.
    """
    return {"status": "ok"}


# Proximos routers entram aqui conforme forem escritos, por exemplo:
# from app.rotas import tenants, clientes, agendamentos
# app.include_router(tenants.router)
# app.include_router(clientes.router)
# app.include_router(agendamentos.router)
