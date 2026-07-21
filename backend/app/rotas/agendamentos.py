"""
Rotas de agendamento (Etapa 5, secao 5.8): so traduzem HTTP. Quem
decide o dominio e app/servicos/agendamentos.py -- esta camada nao
sabe o que e um conflito de horario ou uma transicao invalida, so
sabe transformar os erros de dominio em status HTTP.

Marcar/remarcar/cancelar e permitido para os dois papeis (Etapa 3,
secao 3.5: dono e atendente operam a agenda) -- por isso so
get_usuario_atual, sem exigir_papel.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import get_usuario_atual
from app.core.tenancy import get_tenant_id_atual
from app.database import get_session
from app.schemas.agendamentos import (
    AgendamentoResponse,
    CriarAgendamentoRequest,
    MudarStatusRequest,
)
from app.servicos.agendamentos import criar_agendamento, mudar_status
from app.servicos.erros import (
    ConflitoDeHorarioError,
    ReferenciaDeOutroTenantError,
    TransicaoDeStatusInvalidaError,
)

router = APIRouter(prefix="/agendamentos", tags=["agendamentos"])


@router.post(
    "",
    response_model=AgendamentoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_usuario_atual)],
)
def criar(
    dados: CriarAgendamentoRequest,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> AgendamentoResponse:
    try:
        agendamento = criar_agendamento(
            session,
            tenant_id=tenant_id,
            cliente_id=dados.cliente_id,
            servico_id=dados.servico_id,
            inicio=dados.inicio,
            fim=dados.fim,
        )
    except ReferenciaDeOutroTenantError:
        # Mesmo principio da Etapa 2: nao revela que o cliente/servico
        # existe em outro tenant, trata como se nao existisse (404),
        # nao como "voce nao pode" (403).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cliente ou servico nao encontrado")
    except ConflitoDeHorarioError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    return AgendamentoResponse.model_validate(agendamento)


@router.patch(
    "/{agendamento_id}/status",
    response_model=AgendamentoResponse,
    dependencies=[Depends(get_usuario_atual)],
)
def alterar_status(
    agendamento_id: int,
    dados: MudarStatusRequest,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> AgendamentoResponse:
    try:
        agendamento = mudar_status(session, tenant_id, agendamento_id, dados.status)
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agendamento nao encontrado")
    except TransicaoDeStatusInvalidaError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    return AgendamentoResponse.model_validate(agendamento)
