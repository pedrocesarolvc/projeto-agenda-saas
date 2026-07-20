"""
Cliente — quem recebe o serviço, não quem opera o sistema
(Etapa 4, seção 4.2).

A distinção que confunde no começo: Usuario tem login e marca
horários; Cliente não tem login, é só um registro na agenda. O
barbeiro é usuario; o freguês é cliente. Errar essa distinção embola
a modelagem inteira.

Pertence a um negócio específico -> carrega tenant_id (Etapa 2, seção
2.8), com índice, porque toda consulta de cliente filtra por tenant
(seção 4.6).
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.modelos.tenant import Tenant

if TYPE_CHECKING:
    from app.modelos.agendamento import Agendamento


class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)

    nome: str
    telefone: str | None = None
    email: str | None = None

    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tenant: Tenant = Relationship(back_populates="clientes")
    agendamentos: list["Agendamento"] = Relationship(back_populates="cliente")
