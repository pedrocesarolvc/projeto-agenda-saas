"""
Servico — o que o negócio oferece: nome, duração, preço
(Etapa 1, seção 1.4; Etapa 4, seção 4.2).

duracao_minutos existe porque é dele que o fim de um agendamento é
calculado (seção 4.4: "a duração vem do serviço; o fim é calculado
uma vez, na criação, e gravado" — esse cálculo em si é lógica de
criação de agendamento, Etapa 5/6; aqui só garantimos que o dado
que ele precisa existe).

preco como Numeric(10, 2), não float — dinheiro não se representa em
ponto flutuante binário (erro de arredondamento silencioso). Numeric
é o tipo de precisão exata do Postgres para valores monetários.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.modelos.tenant import Tenant

if TYPE_CHECKING:
    from app.modelos.agendamento import Agendamento


class Servico(SQLModel, table=True):
    __tablename__ = "servicos"

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)

    nome: str
    duracao_minutos: int
    preco: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))

    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tenant: Tenant = Relationship(back_populates="servicos")
    agendamentos: list["Agendamento"] = Relationship(back_populates="servico")
