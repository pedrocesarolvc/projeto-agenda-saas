"""
Pacote "modelos": as entidades do dominio (Etapa 1, secao 1.6).

tenant.py e usuario.py ja existem, no tamanho minimo que a Etapa 3
(autenticacao) exige para login e tenancy funcionarem de verdade.
cliente, servico e agendamento ainda faltam — o desenho relacional
completo, com todas as colunas e relacionamentos, e assunto da
Etapa 4 (Modelagem), ainda pendente de documentacao.

O que ja se sabe, da Etapa 2 (secao 2.8), e a regra que vale para
cada entidade daqui:
"esse dado pertence a um negocio especifico ou ao sistema inteiro?"
Pertence a um negocio (usuario, cliente, servico, agendamento) -> tem
coluna tenant_id. E do sistema (o proprio cadastro de tenants,
configuracao global) -> nao tem — e e exatamente por isso que Tenant,
sozinho, nao carrega tenant_id.

Quando a Etapa 4 for escrita, tenant.py e usuario.py crescem (mais
colunas, relacionamentos) e cliente/servico/agendamento nascem —
nenhum dos dois e recriado do zero.
"""

from app.modelos.tenant import Tenant
from app.modelos.usuario import Papel, Usuario

__all__ = ["Tenant", "Usuario", "Papel"]
