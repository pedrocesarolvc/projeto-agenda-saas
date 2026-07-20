"""
Usuario — quem opera o sistema, não quem é atendido (Etapa 4, seção
4.2: "o barbeiro é usuario; o freguês é cliente").

Nasceu mínimo na Etapa 3 (login precisa de senha, tenant_id e papel —
literalmente as três claims do JWT, seção 3.3). Ganha aqui o
relacionamento de volta para Tenant (seção 4.3).

email é único no sistema inteiro, não por tenant: no v1 uma pessoa
pertence a um único negócio, então o e-mail já basta para o login
achar "de qual tenant este usuário é" (seção 3.3: "está gravado no
cadastro dele").
"""

from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from app.modelos.tenant import Tenant


class Papel(str, Enum):
    """Os dois papéis do v1 (Etapa 3, seção 3.5)."""

    DONO = "dono"
    ATENDENTE = "atendente"


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)

    # Pertence a um negócio específico -> carrega tenant_id
    # (Etapa 2, seção 2.8). É o valor que vai para o claim tenant_id
    # do token (seção 3.3) e que core/tenancy.py consome depois.
    tenant_id: int = Field(foreign_key="tenants.id", index=True)

    nome: str
    email: str = Field(unique=True, index=True)
    senha_hash: str
    papel: Papel

    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tenant: Tenant = Relationship(back_populates="usuarios")
