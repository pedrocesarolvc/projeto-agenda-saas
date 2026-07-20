"""
As duas dependencias que toda rota protegida usa (Etapa 3, secao 3.8):

  get_usuario_atual  -> extrai sub/tenant_id/role do token e entrega
                         "o usuario atual" para a rota (o passo 1 do
                         fluxo da secao 3.5: autenticado?).

  exigir_papel(...)   -> em cima da anterior, barra por papel (o
                          passo 3 do mesmo fluxo: papel permite?).

O texto da secao 3.4 e absoluto e vale repetir aqui, porque e
exatamente o que este arquivo aplica: tenant_id e role NUNCA vem de
um parametro de rota, query string ou corpo de requisicao — vem
SEMPRE do token que o proprio servidor assinou no login. Nenhuma
funcao neste arquivo le Request.query_params ou o corpo da
requisicao para decidir tenant ou papel; so o token.
"""

from dataclasses import dataclass

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decodificar_token
from app.modelos.usuario import Papel

_esquema_bearer = HTTPBearer(auto_error=False)


@dataclass
class UsuarioAtual:
    """O que a Etapa 3 extrai do token: identidade, tenant e papel."""

    id: int
    tenant_id: int
    papel: str


def get_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_esquema_bearer),
) -> UsuarioAtual:
    """
    401 quando "nao sei quem voce e" (secao 3.6): sem header
    Authorization, token adulterado (assinatura nao bate) ou expirado.
    Nunca 403 aqui — 403 e do papel, nao da identidade.
    """
    erro_nao_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciais is None:
        raise erro_nao_autenticado

    try:
        claims = decodificar_token(credenciais.credentials)
    except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError):
        raise erro_nao_autenticado

    return UsuarioAtual(
        id=int(claims["sub"]),
        tenant_id=claims["tenant_id"],
        papel=claims["role"],
    )


def exigir_papel(*papeis_permitidos: Papel):
    """
    Fabrica de dependency para marcar rotas que exigem um papel
    especifico — por exemplo Depends(exigir_papel(Papel.DONO)) na rota
    de criar servico (secao 3.5, tabela de permissoes).

    So roda depois de get_usuario_atual, ou seja, so decide papel para
    quem ja esta autenticado — 403 nunca substitui um 401 que deveria
    ter acontecido antes (secao 3.6).
    """

    def verificador(usuario: UsuarioAtual = Depends(get_usuario_atual)) -> UsuarioAtual:
        if usuario.papel not in {papel.value for papel in papeis_permitidos}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seu papel nao permite esta acao",
            )
        return usuario

    return verificador
