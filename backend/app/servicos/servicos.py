"""
Camada de servico (a de codigo, servicos/) para servico (a entidade,
o item do catalogo -- nome infeliz de coincidir, mas e o vocabulario
do dominio). Etapa 6.

Sem busca aqui de proposito: a secao 6.4 da busca como exemplo para
cliente ("nome contem Silva"); para o catalogo de servicos, so
paginacao e o que a secao 6.3 pede -- "toda listagem pagina, mesmo a
de servicos, que nunca vai ter muitos".
"""

from sqlmodel import Session, select

from app.core.paginacao import ParametrosPaginacao, paginar
from app.core.tenancy import pertence_ao_tenant
from app.modelos.servico import Servico
from app.schemas.servicos import ServicoAtualizar, ServicoCriar
from app.servicos.erros import ReferenciaDeOutroTenantError


def criar_servico(session: Session, tenant_id: int, dados: ServicoCriar) -> Servico:
    servico = Servico(tenant_id=tenant_id, **dados.model_dump())
    session.add(servico)
    session.commit()
    session.refresh(servico)
    return servico


def listar_servicos(
    session: Session, tenant_id: int, parametros: ParametrosPaginacao
) -> tuple[list[Servico], int]:
    query = select(Servico).where(Servico.tenant_id == tenant_id).order_by(Servico.id)
    return paginar(session, query, parametros)


def obter_servico(session: Session, tenant_id: int, servico_id: int) -> Servico:
    servico = session.get(Servico, servico_id)
    if not pertence_ao_tenant(servico, tenant_id):
        raise ReferenciaDeOutroTenantError("servico nao encontrado")
    return servico


def atualizar_servico(
    session: Session, tenant_id: int, servico_id: int, dados: ServicoAtualizar
) -> Servico:
    servico = obter_servico(session, tenant_id, servico_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(servico, campo, valor)
    session.add(servico)
    session.commit()
    session.refresh(servico)
    return servico


def remover_servico(session: Session, tenant_id: int, servico_id: int) -> None:
    servico = obter_servico(session, tenant_id, servico_id)
    session.delete(servico)
    session.commit()
