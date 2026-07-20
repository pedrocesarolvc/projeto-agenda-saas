"""
Configuracao da aplicacao via variavel de ambiente (Etapa 1, secao 1.6).

Nenhum segredo (senha de banco, chave de assinatura de JWT) fica
hardcoded no codigo. Tudo vem do ambiente, com .env.example documentando
quais variaveis existem sem expor valor real nenhum.
"""

import os
from functools import lru_cache


class Settings:
    # URL de conexao com o Postgres. Um unico banco compartilhado por
    # todos os tenants (Etapa 2, secao 2.3-2.4: discriminador de coluna,
    # nao banco por tenant).
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/projeto_agenda",
    )

    # Chave de assinatura do JWT (Etapa 3). app/auth/jwt.py assina e
    # valida com ela o token que carrega usuario, tenant_id e papel —
    # trocar por um valor forte e secreto em producao, nunca usar o
    # default abaixo fora de desenvolvimento local.
    secret_key: str = os.getenv(
        "SECRET_KEY", "changeme-em-producao-use-uma-chave-longa-e-aleatoria"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cache simples para nao reconstruir o objeto de configuracao a
    cada requisicao. Reusado por database.py e, futuramente, por auth/.
    """
    return Settings()
