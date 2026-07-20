"""
Modelo mínimo de Usuario (Etapa 3 empresta o essencial da Etapa 4).

Mesma lógica de tenant.py: o desenho relacional completo é Etapa 4,
mas login (Etapa 3, seção 3.2-3.3) precisa de um usuário de verdade
para conferir senha e descobrir tenant_id e papel. Estas são,
literalmente, as três claims que vão para o JWT (seção 3.3) — nada
aqui é coluna especulativa, é o mínimo que a etapa em mãos exige.

email é único no sistema inteiro, não por tenant: no v1 uma pessoa
pertence a um único negócio, então o e-mail já basta para o login
achar "de qual tenant este usuário é" (seção 3.3: "está gravado no
cadastro dele").
"""

from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


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
