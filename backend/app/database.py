"""
Conexao e sessao do banco (Etapa 1, secao 1.6).

Um unico engine, um unico banco Postgres, compartilhado por todos os
tenants (Etapa 2, secao 2.3-2.4). O isolamento entre negocios NAO
acontece aqui — aqui e so o cano de acesso ao banco. Quem garante que
cada query so ve o dado do tenant certo e a camada central em
app/core/tenancy.py (Etapa 2, secao 2.6, defesa de Nivel 1).
"""

from sqlmodel import Session, create_engine

from app.config import get_settings

settings = get_settings()

# echo=False em producao; ligar para True so quando for depurar SQL.
engine = create_engine(settings.database_url, echo=False)


def get_session():
    """
    Dependency do FastAPI que entrega uma sessao de banco por
    requisicao e garante o fechamento no final.

    Importante: esta funcao NAO filtra por tenant. Ela so abre a
    sessao. O filtro de tenant_id e responsabilidade de
    app/core/tenancy.py, nunca deste arquivo — misturar as duas coisas
    aqui e o tipo de coisa que faz o filtro "se perder" com o tempo
    (Etapa 2, secao 2.5).
    """
    with Session(engine) as session:
        yield session
