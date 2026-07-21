"""
Schemas de entrada/saida de cliente (Etapa 6, secao 6.5 e 6.8).

Tres schemas, de proposito (secao 6.8): criar exige o obrigatorio;
atualizar torna tudo opcional (update parcial, secao 6.6); resposta
so mostra o que o cliente da API deve ver -- sem tenant_id cru.
"""

from pydantic import BaseModel


class ClienteCriar(BaseModel):
    nome: str
    telefone: str | None = None
    email: str | None = None


class ClienteAtualizar(BaseModel):
    """
    Todos os campos opcionais: so o que vier no corpo e alterado
    (update consciente, secao 6.6). tenant_id nem aparece aqui -- nao
    ha campo pelo qual o cliente da API poderia tentar muda-lo.
    """

    nome: str | None = None
    telefone: str | None = None
    email: str | None = None


class ClienteResponse(BaseModel):
    id: int
    nome: str
    telefone: str | None
    email: str | None

    model_config = {"from_attributes": True}
