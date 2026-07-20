"""
Tenant — o negócio, a raiz do isolamento (Etapa 4, seção 4.2).

Nasceu minimo na Etapa 3 (login precisava de um tenant de verdade
para o usuário pertencer); agora ganha os relacionamentos 1:N com
todas as entidades que carregam tenant_id (seção 4.3):

    tenant 1:N usuario, cliente, servico, agendamento

Continua sendo a única tabela do domínio sem tenant_id — Etapa 2,
seção 2.8: ela é a raiz, não pertence a um tenant, ela É o tenant.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modelos.agendamento import Agendamento
    from app.modelos.cliente import Cliente
    from app.modelos.servico import Servico
    from app.modelos.usuario import Usuario


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)
    nome: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    usuarios: list["Usuario"] = Relationship(back_populates="tenant")
    clientes: list["Cliente"] = Relationship(back_populates="tenant")
    servicos: list["Servico"] = Relationship(back_populates="tenant")
    agendamentos: list["Agendamento"] = Relationship(back_populates="tenant")
