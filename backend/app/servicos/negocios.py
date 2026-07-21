"""
Registro de negocio (Etapa 7, secao 7.2): cria o tenant (Etapa 2) e o
primeiro usuario, sempre papel dono (Etapa 3), numa unica operacao.
E o "auth/registrar-negocio" que fecha, na borda da API, o elo entre
"criar um negocio isolado" e "autenticar quem manda nele".
"""

from sqlmodel import Session, select

from app.auth.security import hash_senha
from app.modelos.tenant import Tenant
from app.modelos.usuario import Papel, Usuario
from app.servicos.erros import EmailJaCadastradoError


def registrar_negocio(
    session: Session,
    nome_negocio: str,
    nome_dono: str,
    email: str,
    senha: str,
) -> Usuario:
    ja_existe = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if ja_existe is not None:
        raise EmailJaCadastradoError("e-mail ja cadastrado")

    tenant = Tenant(nome=nome_negocio)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)

    dono = Usuario(
        tenant_id=tenant.id,
        nome=nome_dono,
        email=email,
        senha_hash=hash_senha(senha),
        papel=Papel.DONO,
    )
    session.add(dono)
    session.commit()
    session.refresh(dono)
    return dono
