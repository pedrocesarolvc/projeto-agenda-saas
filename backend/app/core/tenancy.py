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

O ELO COM A ETAPA 3
--------------------
Etapa 3, secao 3.8, e explicita sobre isso: "o tenant_id extraido
[em app/auth/] e o mesmo que a core/tenancy.py (Etapa 2) injeta no
filtro. Autenticacao e isolamento se encontram neste valor — o token
o fornece, a camada de tenancy o consome. Duas etapas, um dado, um
fluxo." get_tenant_id_atual() abaixo e exatamente esse encontro: so
delega para get_usuario_atual (app/auth/dependencies.py) e devolve o
tenant_id que ja veio decodificado do token — nunca lendo URL ou
corpo da requisicao (secao 2.7 e secao 3.4).
"""

from fastapi import Depends

from app.auth.dependencies import UsuarioAtual, get_usuario_atual


def get_tenant_id_atual(usuario: UsuarioAtual = Depends(get_usuario_atual)) -> int:
    """
    A funcao que toda consulta ao banco depende para saber "de qual
    tenant e essa requisicao". O valor vem do token do usuario
    autenticado (claim tenant_id, secao 3.3) — nunca de um parametro
    de URL ou de um campo do corpo da requisicao (secao 2.7: o tenant
    nao e algo que o cliente escolhe, e o servidor quem decide a
    partir de quem esta logado).
    """
    return usuario.tenant_id


def pertence_ao_tenant(registro, tenant_id: int) -> bool:
    """
    Etapa 4, secao 4.5: a chave estrangeira garante que um
    cliente_id/servico_id referenciado por um agendamento EXISTE, mas
    nao que ele pertence ao mesmo tenant do agendamento. Sem essa
    checagem extra, um agendamento do tenant A poderia apontar para
    um cliente do tenant B — um vazamento de tenant escondido dentro
    de uma referencia, o mesmo risco da Etapa 2 (secao 2.5) por outra
    porta.

    Uso pretendido (quando a camada de servico da Etapa 5 existir):
    antes de gravar um agendamento, buscar o Cliente e o Servico
    apontados e confirmar que os dois pertencem ao tenant do usuario
    logado com esta funcao. 'registro' e qualquer objeto com o campo
    tenant_id (Cliente, Servico, Agendamento, Usuario).
    """
    return registro is not None and registro.tenant_id == tenant_id


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
