"""
core/tenancy.py — o ponto unico por onde o filtro de tenant_id e
injetado (Etapa 2, secao 2.6, defesa de Nivel 1).

O QUE ESTE ARQUIVO RESOLVE
---------------------------
Etapa 2 explica que, com discriminador de coluna (tenant_id em cada
tabela), o isolamento entre negocios NAO e automatico: quem separa a
Barbearia A da Barbearia B e o "WHERE tenant_id = :meu_tenant" que
toda query precisa carregar (secao 2.5). Se esse filtro morar
espalhado, escrito a mao, dentro de cada rota, mais cedo ou mais tarde
uma query esquece — e isso e vazamento de dado entre clientes, nao um
bug qualquer.

A defesa (secao 2.6, Nivel 1) e centralizar: nenhuma rota fala com o
banco direto, toda consulta passa por uma camada que recebe o tenant
atual e injeta o filtro sozinha. E exatamente o papel deste modulo.

POR QUE ESTA QUASE VAZIO AINDA
--------------------------------
O filtro depende de saber "quem esta logado e de qual tenant" — e essa
identidade vem do JWT (secao 2.7: "o tenant vem sempre do token, nunca
do que o cliente manda no corpo ou na URL"). A extracao do token e
assunto da Etapa 3 (autenticacao e permissoes), ainda pendente de
documentacao. Por isso get_tenant_id_atual() abaixo e so o contrato —
a implementacao real (decodificar o JWT, validar o usuario) entra
quando a Etapa 3 for escrita.

O motivo de este arquivo existir DESDE JA, mesmo incompleto, e o
mesmo do rodape da documentacao: e mais facil construir centralizado
desde a primeira query do que refatorar vinte queries soltas depois.
"""

from fastapi import Depends


def get_tenant_id_atual() -> str:
    """
    Contrato da funcao que toda consulta ao banco vai depender para
    saber "de qual tenant e essa requisicao".

    Hoje e um placeholder. Quando a Etapa 3 (auth) estiver escrita,
    o corpo desta funcao passa a extrair o tenant_id do JWT do usuario
    autenticado — nunca de um parametro de URL ou de um campo do
    corpo da requisicao (secao 2.7: o tenant nao e algo que o cliente
    escolhe, e o servidor quem decide a partir de quem esta logado).
    """
    raise NotImplementedError(
        "Depende da Etapa 3 (autenticacao): extrair tenant_id do JWT."
    )


def aplicar_filtro_tenant(query, modelo, tenant_id: str):
    """
    Funcao central que toda consulta de dado de negocio (clientes,
    servicos, agendamentos, usuarios) deve passar antes de rodar.

    Ela injeta "WHERE tenant_id = :tenant_id" na query — a parede do
    predio de apartamentos (secao 2.2) — num unico lugar, para que
    nenhuma rota precise (ou possa esquecer de) escrever esse filtro
    a mao.

    'modelo' precisa ter a coluna tenant_id (Etapa 2, secao 2.8: toda
    tabela que pertence a um negocio especifico carrega essa coluna;
    a propria tabela de tenants e configuracao global do sistema sao
    as excecoes).
    """
    return query.where(modelo.tenant_id == tenant_id)


# Dependency pronta para uso nas rotas (quando app/rotas/ existir):
#   def listar_agendamentos(
#       tenant_id: str = Depends(get_tenant_id_atual),
#       session: Session = Depends(get_session),
#   ):
#       query = aplicar_filtro_tenant(select(Agendamento), Agendamento, tenant_id)
#       ...
TenantAtual = Depends(get_tenant_id_atual)


# Reforco de roadmap (Etapa 2, secao 2.6, Nivel 2): alem desta camada
# central, o Postgres oferece Row-Level Security (RLS), que faz o
# proprio banco recusar devolver linha de outro tenant mesmo se uma
# query esquecer o filtro. Fica fora do v1 pelo custo de configuracao
# e depuracao, mas e a defesa estrutural que este modulo aproxima.
