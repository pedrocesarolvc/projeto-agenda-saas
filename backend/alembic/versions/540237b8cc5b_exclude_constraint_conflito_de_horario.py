"""exclude constraint conflito de horario

Etapa 5, secao 5.6: a defesa robusta contra a race condition da
secao 5.5. A verificacao em codigo (app/servicos/agendamentos.py)
existe para dar uma mensagem de erro amigavel no caso comum; esta
constraint existe para garantir a correcao no caso raro de
concorrencia real -- o banco recusa a segunda insercao mesmo que duas
requisicoes tenham passado pela verificacao ao mesmo tempo.

EXCLUDE USING gist e btree_gist sao recursos exclusivos do
PostgreSQL (nao existem em SQLite, usado nos testes locais deste
projeto por conveniencia -- Etapa 1, secao 1.5). Por isso todo o
corpo deste arquivo e guardado por dialeto: em Postgres, cria a
extensao e a constraint de verdade; em qualquer outro banco, e um
no-op -- o upgrade/downgrade continua aplicando e revertendo sem
erro (o teste da Etapa 4, secao 4.8), so que sem a garantia extra,
que so faz sentido pedir ao motor que realmente a oferece.

A condicao "tenant_id WITH =" e o que faz dois agendamentos em
tenants diferentes NUNCA colidirem aqui -- o isolamento da Etapa 2
entra na propria constraint, nao so nas queries do servico.
"WHERE (status <> 'cancelado')" e a mesma regra da secao 5.4: um
agendamento cancelado libera o horario.

Revision ID: 540237b8cc5b
Revises: 4daf712f87bb
Create Date: 2026-07-20 20:50:47.524625

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '540237b8cc5b'
down_revision: Union[str, Sequence[str], None] = '4daf712f87bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE agendamentos
        ADD CONSTRAINT ck_agendamentos_sem_sobreposicao
        EXCLUDE USING gist (
            tenant_id WITH =,
            tstzrange(inicio, fim) WITH &&
        )
        WHERE (status <> 'cancelado')
        """
    )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    op.execute("ALTER TABLE agendamentos DROP CONSTRAINT ck_agendamentos_sem_sobreposicao")
    # A extensao btree_gist nao e removida de proposito: pode ter
    # sido criada por, ou estar em uso por, outra parte do banco.
