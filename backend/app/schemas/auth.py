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


class RegistrarNegocioRequest(BaseModel):
    """
    Etapa 7, secao 7.2: cria o tenant (Etapa 2) e o primeiro usuario,
    sempre papel dono (Etapa 3) -- quem registra o negocio e quem
    manda nele. Devolve token direto (TokenResponse): registrar ja
    deixa a pessoa logada, a "porta de entrada limpa" da secao 7.3.
    """

    nome_negocio: str
    nome_dono: str
    email: str
    senha: str
