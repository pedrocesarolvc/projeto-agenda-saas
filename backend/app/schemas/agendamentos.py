"""
Formato de entrada/saida das rotas de agendamento (Etapa 5).
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


class AgendamentoResponse(BaseModel):
    id: int
    cliente_id: int
    servico_id: int
    inicio: datetime
    fim: datetime
    status: str

    model_config = {"from_attributes": True}
