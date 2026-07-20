"""
Pacote "modelos": as entidades do dominio (Etapa 1, secao 1.6).

Vai receber tenant, usuario, cliente, servico e agendamento — o
desenho relacional completo e assunto da Etapa 4 (Modelagem), ainda
pendente de documentacao. Por isso a pasta existe mas nao tem
nenhuma classe de modelo ainda: criar entidade sem a etapa que define
as colunas e relacionamentos seria adivinhar o desenho.

O que ja se sabe, da Etapa 2 (secao 2.8), e a regra que vai valer
para cada entidade daqui quando forem escritas:
"esse dado pertence a um negocio especifico ou ao sistema inteiro?"
Pertence a um negocio (usuario, cliente, servico, agendamento) -> tem
coluna tenant_id. E do sistema (o proprio cadastro de tenants,
configuracao global) -> nao tem.
"""
