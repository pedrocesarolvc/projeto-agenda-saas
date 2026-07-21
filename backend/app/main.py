"""
Ponto de entrada da API (Etapa 1, secao 1.6).

Responsabilidade unica deste arquivo: subir a instancia do FastAPI e
registrar os routers (os arquivos de app/rotas/) conforme eles vao
existindo. auth.py e o primeiro (Etapa 3); agendamentos.py chega com
a Etapa 5; clientes.py e servicos.py chegam com o CRUD de producao
da Etapa 6; tenants.py chega com a Etapa 7.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.rotas import agendamentos, auth, clientes, servicos, tenants

app = FastAPI(
    title="Projeto Agenda - SaaS de Agendamento Multi-tenant",
    version="0.1.0",
)

# A interface (Etapa 7) roda em outra origem (porta do Vite/nginx) --
# sem isso o navegador bloqueia as chamadas por CORS. Autenticacao e
# via Bearer token no header, nao cookie, entao nao precisa de
# allow_credentials nem restringir origem por sessao.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tenants.router)
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
