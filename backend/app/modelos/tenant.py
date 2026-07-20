"""
Modelo mínimo de Tenant (Etapa 3 empresta o essencial da Etapa 4).

O desenho relacional completo — todas as colunas, relacionamentos e
constraints de cada entidade — é assunto da Etapa 4 (Modelagem), ainda
pendente de documentação. Mas a Etapa 3 (autenticação) não roda sem um
tenant de verdade para o usuário pertencer: o login grava o tenant_id
no token (seção 3.3), e esse tenant_id tem que apontar pra algo no
banco. Por isso este arquivo nasce agora, do tamanho mínimo que a
Etapa 3 exige — não é o desenho final, é o suficiente pra login e
tenancy funcionarem de verdade.

Quando a Etapa 4 for escrita, este arquivo cresce (mais colunas,
relacionamentos com clientes/serviços/agendamentos), não é recriado.
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"

    # Único ponto do domínio sem tenant_id — Etapa 2, seção 2.8:
    # a própria tabela de tenants existe "acima" dos tenants.
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
