"""
Fixtures compartilhadas pelos testes das Etapas 3 e 4.

Banco: SQLite em memoria, recriado a cada teste (StaticPool mantem a
mesma conexao entre as chamadas dentro de um teste). Nao precisa de
Postgres rodando so para validar login, permissao e modelagem.

SQLite nao aplica chave estrangeira por padrao -- precisa do PRAGMA
abaixo ligado por conexao, senao o teste "FK barra id inexistente"
(Etapa 4, secao 4.8) passaria por engano mesmo com a constraint
ausente em tempo de execucao.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth.security import hash_senha
from app.database import get_session
from app.main import app
from app.modelos.cliente import Cliente
from app.modelos.servico import Servico
from app.modelos.tenant import Tenant
from app.modelos.usuario import Papel, Usuario


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _ligar_fk(conexao_dbapi, _):
        conexao_dbapi.execute("PRAGMA foreign_keys=ON")

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def criar_tenant(session: Session, nome: str = "Barbearia A") -> Tenant:
    tenant = Tenant(nome=nome)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


def criar_usuario(
    session: Session,
    tenant_id: int,
    email: str,
    senha: str = "senha-correta",
    papel: Papel = Papel.DONO,
) -> Usuario:
    usuario = Usuario(
        tenant_id=tenant_id,
        nome="Usuario de teste",
        email=email,
        senha_hash=hash_senha(senha),
        papel=papel,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def criar_cliente(session: Session, tenant_id: int, nome: str = "Cliente de teste") -> Cliente:
    cliente = Cliente(tenant_id=tenant_id, nome=nome)
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente


def autenticar(client: TestClient, email: str, senha: str = "senha-correta") -> dict:
    """Login via rota real e devolve o header Authorization pronto,
    para os testes de CRUD (Etapa 6) que batem na API de verdade."""
    token = client.post("/auth/login", json={"email": email, "senha": senha}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def criar_servico(
    session: Session,
    tenant_id: int,
    nome: str = "Corte",
    duracao_minutos: int = 30,
    preco: str = "50.00",
) -> Servico:
    servico = Servico(
        tenant_id=tenant_id,
        nome=nome,
        duracao_minutos=duracao_minutos,
        preco=preco,
    )
    session.add(servico)
    session.commit()
    session.refresh(servico)
    return servico
