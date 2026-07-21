"""
Agendamento — a entidade central do domínio (Etapa 4, seção 4.3-4.4):
onde cliente, serviço e tempo se encontram, e sobre a qual a regra de
negócio da Etapa 5 (conflito de horário, transição de status) vai
operar.

Três decisões da seção 4.4, nenhuma arbitrária:

  inicio/fim, não inicio+duração
      Torna a detecção de conflito (Etapa 5) uma comparação direta
      entre intervalos. Guardar só o início e a duração faria toda
      checagem de sobreposição recalcular o fim — trabalho repetido
      e fonte de erro.

  DateTime(timezone=True) -> TIMESTAMPTZ no Postgres
      Tempo sem fuso é ambíguo. Convenção da aplicação: todo datetime
      é gravado e lido em UTC; conversão para o fuso do usuário é
      responsabilidade da camada de apresentação, não do banco.

  status como texto com default "marcado"
      O ciclo de vida (marcado -> concluído / cancelado) é regra de
      negócio da Etapa 5. A coluna só guarda o estado atual; as
      transições válidas não são impostas aqui.

Índice composto (seção 4.6): a pergunta "existe agendamento neste
tenant que se sobreponha a este intervalo?" (Etapa 5) é sobre
(tenant_id, inicio, fim) — é para ela que o índice abaixo existe.
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Index
from sqlmodel import Field, Relationship, SQLModel

from app.modelos.cliente import Cliente
from app.modelos.servico import Servico
from app.modelos.tenant import Tenant


class StatusAgendamento(str, Enum):
    """
    O vocabulario dos tres estados da secao 5.7. Deliberadamente NAO
    e o tipo da coluna `status` no banco -- ela continua sendo texto
    puro (Etapa 4, seção 4.4: "as transições válidas não são impostas
    aqui" no banco). Isto so existe para a camada de servico (Etapa 5)
    ter valores nomeados em vez de strings soltas espalhadas pelo
    codigo.
    """

    MARCADO = "marcado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Agendamento(SQLModel, table=True):
    __tablename__ = "agendamentos"
    __table_args__ = (
        Index("ix_agendamentos_tenant_intervalo", "tenant_id", "inicio", "fim"),
    )

    id: int | None = Field(default=None, primary_key=True)

    # As referências da seção 4.5: a FK garante que cliente_id e
    # servico_id EXISTEM, mas não que pertencem a este mesmo tenant.
    # Quem garante isso é core.tenancy.pertence_ao_tenant(), chamado
    # pela camada de serviço (Etapa 5) antes de gravar.
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    cliente_id: int = Field(foreign_key="clientes.id")
    servico_id: int = Field(foreign_key="servicos.id")

    inicio: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    fim: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    status: str = Field(default=StatusAgendamento.MARCADO.value)

    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tenant: Tenant = Relationship(back_populates="agendamentos")
    cliente: Cliente = Relationship(back_populates="agendamentos")
    servico: Servico = Relationship(back_populates="agendamentos")
