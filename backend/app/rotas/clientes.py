"""
Rotas de cliente (Etapa 6). So traduzem HTTP: paginacao e busca vem
de query params, erro de dominio vira status HTTP.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import get_usuario_atual
from app.core.paginacao import Pagina, ParametrosPaginacao, parametros_paginacao
from app.core.tenancy import get_tenant_id_atual
from app.database import get_session
from app.schemas.clientes import ClienteAtualizar, ClienteCriar, ClienteResponse
from app.servicos.clientes import (
    atualizar_cliente,
    criar_cliente,
    listar_clientes,
    obter_cliente,
    remover_cliente,
)
from app.servicos.erros import ReferenciaDeOutroTenantError

router = APIRouter(prefix="/clientes", tags=["clientes"], dependencies=[Depends(get_usuario_atual)])


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar(
    dados: ClienteCriar,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> ClienteResponse:
    return ClienteResponse.model_validate(criar_cliente(session, tenant_id, dados))


@router.get("", response_model=Pagina[ClienteResponse])
def listar(
    busca: str | None = None,
    parametros: ParametrosPaginacao = Depends(parametros_paginacao),
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> Pagina[ClienteResponse]:
    itens, total = listar_clientes(session, tenant_id, parametros, busca)
    return Pagina[ClienteResponse](
        itens=[ClienteResponse.model_validate(item) for item in itens],
        total=total,
        pagina=parametros.pagina,
        tamanho_pagina=parametros.tamanho_pagina,
    )


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter(
    cliente_id: int,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> ClienteResponse:
    try:
        return ClienteResponse.model_validate(obter_cliente(session, tenant_id, cliente_id))
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cliente nao encontrado")


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar(
    cliente_id: int,
    dados: ClienteAtualizar,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> ClienteResponse:
    try:
        return ClienteResponse.model_validate(
            atualizar_cliente(session, tenant_id, cliente_id, dados)
        )
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cliente nao encontrado")


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    cliente_id: int,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> None:
    try:
        remover_cliente(session, tenant_id, cliente_id)
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cliente nao encontrado")
