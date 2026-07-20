"""
Etapa 4, secao 4.7: Alembic versiona o schema (uma migration por
mudanca de estrutura, aplicavel e reversivel), em vez de recriar o
banco do zero a cada alteracao.

Duas escolhas deste arquivo, sobre o padrao gerado por `alembic init`:

1. target_metadata aponta para SQLModel.metadata, depois de importar
   app.modelos (que importa as 5 entidades) -- e o que liga
   `alembic revision --autogenerate` ao desenho real das tabelas.

2. A URL de conexao NAO fica duplicada em alembic.ini. Ela vem de
   app.config.get_settings().database_url, a mesma fonte que
   app/database.py usa -- um unico lugar define onde o banco esta.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from app.config import get_settings
import app.modelos  # noqa: F401 -- importa as 5 entidades, popula o metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# Sobrescreve o sqlalchemy.url do alembic.ini (deixado em branco) com
# o DATABASE_URL da aplicacao.
config.set_main_option("sqlalchemy.url", get_settings().database_url)


def run_migrations_offline() -> None:
    """Gera o SQL sem se conectar a um banco (alembic upgrade --sql)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta de verdade e aplica a migration (o caso comum)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
