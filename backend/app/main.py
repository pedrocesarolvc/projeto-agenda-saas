"""
Ponto de entrada da API (Etapa 1, secao 1.6).

Responsabilidade unica deste arquivo: subir a instancia do FastAPI e
registrar os routers (os arquivos de app/rotas/) quando eles existirem.

Por que ainda nao ha nenhum router registrado aqui:
app/rotas/ so nasce quando o primeiro recurso (ex.: tenants, usuarios)
tiver rota de verdade para expor — nao se cria pasta vazia esperando
o futuro (Etapa 1, secao 1.6). Este arquivo cresce junto.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Projeto Agenda - SaaS de Agendamento Multi-tenant",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    """
    Endpoint minimo de verificacao de vida da API.
    Nao pertence a nenhum tenant (nao tem tenant_id) porque nao
    acessa dado de negocio nenhum — so confirma que o processo esta de pe.
    """
    return {"status": "ok"}


# Quando app/rotas/ existir, o registro entra aqui, por exemplo:
# from app.rotas import tenants, usuarios, agendamentos
# app.include_router(tenants.router)
# app.include_router(usuarios.router)
# app.include_router(agendamentos.router)
