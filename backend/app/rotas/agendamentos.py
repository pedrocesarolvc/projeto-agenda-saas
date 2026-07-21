"""
Rotas de agendamento (Etapas 5 e 6): so traduzem HTTP. Quem decide o
dominio e app/servicos/agendamentos.py -- esta camada nao sabe o que
e um conflito de horario ou uma transicao invalida, so sabe
transformar os erros de dominio em status HTTP (404/409).

Marcar/remarcar/cancelar e permitido para os dois papeis (Etapa 3,
secao 3.5: dono e atendente operam a agenda) -- por isso so
get_usuario_atual, sem exigir_papel.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import get_usuario_atual
from app.core.paginacao import Pagina, ParametrosPaginacao, parametros_paginacao
from app.core.tenancy import get_tenant_id_atual
from app.database import get_session
from app.modelos.agendamento import StatusAgendamento
from app.schemas.agendamentos import (
    AgendamentoResponse,
    CriarAgendamentoRequest,
    MudarStatusRequest,
    RemarcarAgendamentoRequest,
)
from app.servicos.agendamentos import (
    criar_agendamento,
    listar_agendamentos,
    mudar_status,
    obter_agendamento,
    remarcar_agendamento,
)
from app.servicos.erros import (
    ConflitoDeHorarioError,
    ReferenciaDeOutroTenantError,
    TransicaoDeStatusInvalidaError,
)

router = APIRouter(
    prefix="/agendamentos", tags=["agendamentos"], dependencies=[Depends(get_usuario_atual)]
)


@router.post("", response_model=AgendamentoResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=Pagina[AgendamentoResponse])
def listar(
    status_filtro: StatusAgendamento | None = None,
    dia: date | None = None,
    cliente: str | None = None,
    parametros: ParametrosPaginacao = Depends(parametros_paginacao),
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> Pagina[AgendamentoResponse]:
    """
    status_filtro e dia sao filtro (recorte exato); cliente e busca
    (nome parcial). Os tres sao opcionais e combinaveis (secao 6.4).
    """
    itens, total = listar_agendamentos(
        session, tenant_id, parametros, status_filtro=status_filtro, dia=dia, busca_cliente=cliente
    )
    return Pagina[AgendamentoResponse](
        itens=[AgendamentoResponse.model_validate(item) for item in itens],
        total=total,
        pagina=parametros.pagina,
        tamanho_pagina=parametros.tamanho_pagina,
    )


@router.get("/{agendamento_id}", response_model=AgendamentoResponse)
def obter(
    agendamento_id: int,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> AgendamentoResponse:
    try:
        return AgendamentoResponse.model_validate(
            obter_agendamento(session, tenant_id, agendamento_id)
        )
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agendamento nao encontrado")


@router.patch("/{agendamento_id}/status", response_model=AgendamentoResponse)
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


@router.patch("/{agendamento_id}", response_model=AgendamentoResponse)
def remarcar(
    agendamento_id: int,
    dados: RemarcarAgendamentoRequest,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> AgendamentoResponse:
    try:
        agendamento = remarcar_agendamento(
            session, tenant_id, agendamento_id, dados.inicio, dados.fim
        )
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agendamento nao encontrado")
    except ConflitoDeHorarioError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    return AgendamentoResponse.model_validate(agendamento)
