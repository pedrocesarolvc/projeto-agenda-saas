"""
Schemas de entrada/saida de servico (o item do catalogo, Etapa 6).

gt=0 em duracao_minutos e preco e a validacao de formato da secao
6.5: o Pydantic barra um preco negativo ou uma duracao zero antes de
qualquer logica de dominio rodar, com 422 e mensagem clara.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class ServicoCriar(BaseModel):
    nome: str
    duracao_minutos: int = Field(gt=0)
    preco: Decimal = Field(gt=0)


class ServicoAtualizar(BaseModel):
    """Update parcial (secao 6.6): tudo opcional, so o enviado muda."""

    nome: str | None = None
    duracao_minutos: int | None = Field(default=None, gt=0)
    preco: Decimal | None = Field(default=None, gt=0)


class ServicoResponse(BaseModel):
    id: int
    nome: str
    duracao_minutos: int
    preco: Decimal

    model_config = {"from_attributes": True}
