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

    # Etapa 7, secao 7.3: o calendario precisa mostrar QUEM e O QUE,
    # nao so ids -- "Corte com Fulano", nao "Agendamento #4". Nao vem
    # de graca do model_validate(agendamento) (nao sao atributos do
    # Agendamento em si); rotas/agendamentos.py monta isso a partir
    # dos relacionamentos (Etapa 4) antes de devolver.
    cliente_nome: str
    servico_nome: str

    model_config = {"from_attributes": True}
