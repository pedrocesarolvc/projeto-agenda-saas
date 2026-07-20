"""
Fixtures compartilhadas pelos testes da Etapa 3.

Banco: SQLite em memoria, recriado a cada teste (StaticPool mantem a
mesma conexao entre as chamadas dentro de um teste). Nao precisa de
Postgres rodando so para validar login e permissao.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth.security import hash_senha
from app.database import get_session
from app.main import app
from app.modelos.tenant import Tenant
from app.modelos.usuario import Papel, Usuario


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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
