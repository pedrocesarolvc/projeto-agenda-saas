"""
Emissao e validacao do JWT (Etapa 3, secao 3.2-3.3).

O payload carrega exatamente as tres claims descritas na secao 3.3:

    sub: id do usuario        <- quem e voce
    tenant_id: id do negocio  <- de qual negocio voce e
    role: "dono"/"atendente"  <- seu papel (secao 3.5)

Nada alem disso entra no token. Em particular, nao existe nenhum jeito
de o CLIENTE escolher o que vai nessas claims — quem preenche e sempre
o backend, no momento do login, a partir do que esta gravado no
cadastro do usuario (secao 3.4).
"""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_settings

ALGORITMO = "HS256"
EXPIRA_EM_MINUTOS = 60 * 8  # sessao de 8 horas


def criar_token(usuario_id: int, tenant_id: int, papel: str) -> str:
    """
    Emitido uma unica vez, no login (secao 3.2), depois que a senha
    ja foi conferida. Tudo que vem depois nesta requisicao — e em
    toda requisicao seguinte que carregar este token — confia nestas
    claims sem reconsultar o banco.
    """
    settings = get_settings()
    agora = datetime.now(timezone.utc)

    payload = {
        "sub": str(usuario_id),
        "tenant_id": tenant_id,
        "role": papel,
        "iat": agora,
        "exp": agora + timedelta(minutes=EXPIRA_EM_MINUTOS),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITMO)


def decodificar_token(token: str) -> dict:
    """
    Valida a assinatura e a expiracao. Deixa propagar
    jwt.ExpiredSignatureError (token vencido) e jwt.InvalidTokenError
    (assinatura nao bate — token adulterado ou forjado) para quem
    chamou decidir o que responder; em app/auth/dependencies.py isso
    vira 401 (secao 3.6).
    """
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO])
