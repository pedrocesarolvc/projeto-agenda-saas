"""
Rotas de autenticacao (Etapa 3).

POST /auth/login  -> confere credenciais, emite o token (secao 3.2-3.3)
GET  /auth/me      -> devolve o que get_usuario_atual extraiu do token;
                      existe para toda outra rota protegida seguir o
                      mesmo padrao (Depends(get_usuario_atual)).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.dependencies import UsuarioAtual, get_usuario_atual
from app.auth.jwt import criar_token
from app.auth.security import verificar_senha
from app.database import get_session
from app.modelos.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["autenticacao"])


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()

    # Mesma mensagem para "email nao existe" e "senha errada" — nao dar
    # pista de qual das duas coisas o cliente errou (evita enumerar
    # e-mails cadastrados por tentativa e erro).
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas",
    )

    if usuario is None or not verificar_senha(dados.senha, usuario.senha_hash):
        raise credenciais_invalidas

    token = criar_token(
        usuario_id=usuario.id,
        tenant_id=usuario.tenant_id,
        papel=usuario.papel.value,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UsuarioAtual)
def eu(usuario: UsuarioAtual = Depends(get_usuario_atual)) -> UsuarioAtual:
    """
    Ilustra o padrao que toda rota protegida futura vai seguir: pedir
    Depends(get_usuario_atual) e receber id/tenant_id/papel prontos,
    sem tocar em JWT nenhum na propria rota.
    """
    return usuario
