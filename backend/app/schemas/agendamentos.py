"""
Formato de entrada/saida das rotas de agendamento (Etapas 5 e 6).
"""

from datetime import datetime

from pydantic import BaseModel

from app.modelos.agendamento import StatusAgendamento


class CriarAgendamentoRequest(BaseModel):
    cliente_id: int
    servico_id: int
    inicio: datetime
    fim: datetime


class MudarStatusRequest(BaseModel):
    status: StatusAgendamento


class RemarcarAgendamentoRequest(BaseModel):
    """
    Etapa 6, secao 6.6: so inicio/fim. Nem tenant_id nem status
    aparecem aqui -- o primeiro nunca se atualiza, o segundo tem rota
    propria (MudarStatusRequest). Nao e um update generico do
    agendamento inteiro; e a operacao especifica "remarcar".
    """

    inicio: datetime
    fim: datetime


class AgendamentoResponse(BaseModel):
    id: int
    cliente_id: int
    servico_id: int
    inicio: datetime
    fim: datetime
    status: str

    model_config = {"from_attributes": True}
