"""
Camada de servico para cliente (Etapa 6).

Cliente nao tem regra de dominio como a de agendamento (sem conflito,
sem maquina de estados) -- mesmo assim mora em servicos/, nao na
rota: testavel sem subir a API, e o update consciente (secao 6.6)
fica num lugar so, nao espalhado pelas rotas.
"""

from sqlmodel import Session, select

from app.core.paginacao import ParametrosPaginacao, paginar
from app.core.tenancy import pertence_ao_tenant
from app.modelos.cliente import Cliente
from app.schemas.clientes import ClienteAtualizar, ClienteCriar
from app.servicos.erros import ReferenciaDeOutroTenantError


def criar_cliente(session: Session, tenant_id: int, dados: ClienteCriar) -> Cliente:
    cliente = Cliente(tenant_id=tenant_id, **dados.model_dump())
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente


def listar_clientes(
    session: Session,
    tenant_id: int,
    parametros: ParametrosPaginacao,
    busca: str | None = None,
) -> tuple[list[Cliente], int]:
    """Secao 6.4: tenant_id sempre primeiro; busca por nome parcial
    (ILIKE) e opcional -- so restringe se veio."""
    query = select(Cliente).where(Cliente.tenant_id == tenant_id)
    if busca:
        query = query.where(Cliente.nome.ilike(f"%{busca}%"))
    query = query.order_by(Cliente.id)
    return paginar(session, query, parametros)


def obter_cliente(session: Session, tenant_id: int, cliente_id: int) -> Cliente:
    cliente = session.get(Cliente, cliente_id)
    if not pertence_ao_tenant(cliente, tenant_id):
        raise ReferenciaDeOutroTenantError("cliente nao encontrado")
    return cliente


def atualizar_cliente(
    session: Session, tenant_id: int, cliente_id: int, dados: ClienteAtualizar
) -> Cliente:
    cliente = obter_cliente(session, tenant_id, cliente_id)
    # So os campos enviados mudam (update parcial, secao 6.6).
    # tenant_id nem existe em ClienteAtualizar -- nao ha por onde
    # tentar move-lo de negocio por aqui.
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente


def remover_cliente(session: Session, tenant_id: int, cliente_id: int) -> None:
    cliente = obter_cliente(session, tenant_id, cliente_id)
    session.delete(cliente)
    session.commit()
