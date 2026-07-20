"""
Formato de entrada/saida da rota de login (Etapa 3, secao 3.2).

Reparem no que NAO existe aqui: nenhum campo tenant_id. LoginRequest
so pede email e senha porque o cliente diz "quem quer autenticar", e
o servidor e quem decide o tenant a partir do cadastro do usuario
(secao 3.4) — nao ha campo nenhum pelo qual o cliente poderia tentar
influenciar isso.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
