"""
Paginacao reutilizavel (Etapa 6, secao 6.3 e 6.8).

O ponto da secao 6.3: "toda listagem pagina, sem excecao" -- inclusive
a de servicos, que "nunca vai ter muitos" (a suposicao que envelhece
pior em software). Por isso isto mora em core/, ao lado de tenancy.py:
e a mesma logica -- um lugar so, para nenhuma rota reinventar
limit/offset (ou esquecer o teto).
"""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlmodel import Session, func, select

TAMANHO_PAGINA_PADRAO = 20

# O teto da secao 6.3: sem ele, limit=999999 derruba justamente o que
# a paginacao existe para proteger (banco, memoria, rede).
TAMANHO_PAGINA_MAXIMO = 100

T = TypeVar("T")


class ParametrosPaginacao(BaseModel):
    pagina: int
    tamanho_pagina: int

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamanho_pagina


def parametros_paginacao(
    pagina: int = Query(default=1, ge=1, description="pagina, comeca em 1"),
    tamanho_pagina: int = Query(
        default=TAMANHO_PAGINA_PADRAO,
        ge=1,
        le=TAMANHO_PAGINA_MAXIMO,
        description=f"maximo {TAMANHO_PAGINA_MAXIMO} -- pedir mais e limitado ao teto, nao obedecido cego",
    ),
) -> ParametrosPaginacao:
    return ParametrosPaginacao(pagina=pagina, tamanho_pagina=tamanho_pagina)


class Pagina(BaseModel, Generic[T]):
    """
    O contrato de toda resposta paginada: os itens da pagina atual,
    mais total/pagina/tamanho_pagina para o frontend montar a
    navegacao (secao 6.3).
    """

    itens: list[T]
    total: int
    pagina: int
    tamanho_pagina: int


def paginar(session: Session, query, parametros: ParametrosPaginacao) -> tuple[list, int]:
    """
    Aplica limit/offset a uma query ja filtrada (por tenant e por
    quaisquer filtros/busca) e devolve os itens da pagina junto do
    total de registros que a query inteira bateria -- sem o total,
    o frontend nao sabe quantas paginas existem.
    """
    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    itens = session.exec(query.offset(parametros.offset).limit(parametros.tamanho_pagina)).all()
    return itens, total
