"""
Erros de dominio das Etapas 5, 6 e 7 -- nao sao excecoes HTTP. A
camada de servico (secao 5.8) nao sabe que HTTP existe; quem traduz
isso em 404/409/422 e a rota, nao o servico.
"""


class ConflitoDeHorarioError(Exception):
    """O intervalo pedido se sobrepoe a um agendamento existente do
    mesmo tenant (secao 5.3-5.4)."""


class ReferenciaDeOutroTenantError(Exception):
    """
    Um registro (cliente, servico, agendamento) nao existe ou nao
    pertence ao tenant do usuario logado (Etapa 4, secao 4.5).

    Os dois casos -- "nao existe" e "existe, mas e de outro tenant"
    -- viram o mesmo erro de proposito: de fora, ninguem deve
    conseguir distinguir "esse id nunca existiu" de "esse id e de
    outro negocio". As duas viram 404 na rota (Etapa 2 outra vez, na
    borda HTTP)."""


class TransicaoDeStatusInvalidaError(Exception):
    """A mudanca de status pedida nao e uma aresta valida da maquina
    de estados (secao 5.7)."""


class EmailJaCadastradoError(Exception):
    """POST /auth/registrar-negocio com um e-mail que ja tem usuario
    (Etapa 7, secao 7.2). email e unico no sistema inteiro (Etapa 3,
    seção 3.3), entao isso e um 409, nao um 422 -- o dado esta bem
    formado, so ja existe."""
