"""
Pacote "modelos": as cinco entidades do dominio (Etapa 4, secao 4.2).

    tenant 1:N usuario, cliente, servico, agendamento
    agendamento N:1 cliente, N:1 servico  (secao 4.3)

Import de todas as classes aqui, num lugar so, e o que garante que o
registro de mapeamento do SQLModel/SQLAlchemy resolve as referencias
em string (ex.: Relationship(back_populates="clientes")) usadas nos
arquivos individuais — cada modulo importa so o que precisa
diretamente (evitando import circular) e conta com este __init__
carregar o resto antes de qualquer query rodar.

A regra que decide quem carrega tenant_id, da Etapa 2 (secao 2.8):
"esse dado pertence a um negocio especifico ou ao sistema inteiro?"
So Tenant fica de fora — ele e a raiz, nao pertence a um tenant, ele
E o tenant.
"""

from app.modelos.agendamento import Agendamento, StatusAgendamento
from app.modelos.cliente import Cliente
from app.modelos.servico import Servico
from app.modelos.tenant import Tenant
from app.modelos.usuario import Papel, Usuario

__all__ = [
    "Tenant",
    "Usuario",
    "Papel",
    "Cliente",
    "Servico",
    "Agendamento",
    "StatusAgendamento",
]
