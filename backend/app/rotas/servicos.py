"""
Rotas de servico (o item do catalogo, Etapa 6).

Etapa 3, secao 3.5, ja tinha decidido isto na tabela de permissoes:
"Criar / editar / remover servicos e precos" e dono, nao atendente.
A Etapa 6 criou o CRUD sem aplicar essa linha; a revisao de
coerencia da Etapa 7 (secao 7.2) e onde isso e pego -- exigir_papel
so entra nas tres rotas de escrita. Listar/obter continuam abertas
aos dois papeis: o atendente precisa VER os servicos para marcar um
agendamento, so nao pode alterar o catalogo.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import exigir_papel, get_usuario_atual
from app.core.paginacao import Pagina, ParametrosPaginacao, parametros_paginacao
from app.core.tenancy import get_tenant_id_atual
from app.database import get_session
from app.modelos.usuario import Papel
from app.schemas.servicos import ServicoAtualizar, ServicoCriar, ServicoResponse
from app.servicos.erros import ReferenciaDeOutroTenantError
from app.servicos.servicos import (
    atualizar_servico,
    criar_servico,
    listar_servicos,
    obter_servico,
    remover_servico,
)

router = APIRouter(prefix="/servicos", tags=["servicos"], dependencies=[Depends(get_usuario_atual)])


@router.post(
    "",
    response_model=ServicoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_papel(Papel.DONO))],
)
def criar(
    dados: ServicoCriar,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> ServicoResponse:
    return ServicoResponse.model_validate(criar_servico(session, tenant_id, dados))


@router.get("", response_model=Pagina[ServicoResponse])
def listar(
    parametros: ParametrosPaginacao = Depends(parametros_paginacao),
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> Pagina[ServicoResponse]:
    itens, total = listar_servicos(session, tenant_id, parametros)
    return Pagina[ServicoResponse](
        itens=[ServicoResponse.model_validate(item) for item in itens],
        total=total,
        pagina=parametros.pagina,
        tamanho_pagina=parametros.tamanho_pagina,
    )


@router.get("/{servico_id}", response_model=ServicoResponse)
def obter(
    servico_id: int,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> ServicoResponse:
    try:
        return ServicoResponse.model_validate(obter_servico(session, tenant_id, servico_id))
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="servico nao encontrado")


@router.put(
    "/{servico_id}",
    response_model=ServicoResponse,
    dependencies=[Depends(exigir_papel(Papel.DONO))],
)
def atualizar(
    servico_id: int,
    dados: ServicoAtualizar,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> ServicoResponse:
    try:
        return ServicoResponse.model_validate(
            atualizar_servico(session, tenant_id, servico_id, dados)
        )
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="servico nao encontrado")


@router.delete(
    "/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_papel(Papel.DONO))],
)
def remover(
    servico_id: int,
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> None:
    try:
        remover_servico(session, tenant_id, servico_id)
    except ReferenciaDeOutroTenantError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="servico nao encontrado")
