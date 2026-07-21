"""
Erros de dominio da Etapa 5 -- nao sao excecoes HTTP. A camada de
servico (secao 5.8) nao sabe que HTTP existe; quem traduz isso em
409/422 e a rota, nao o servico.
"""


class ConflitoDeHorarioError(Exception):
    """O intervalo pedido se sobrepoe a um agendamento existente do
    mesmo tenant (secao 5.3-5.4)."""


class ReferenciaDeOutroTenantError(Exception):
    """cliente_id ou servico_id nao pertence ao tenant do usuario
    logado (Etapa 4, secao 4.5)."""


class TransicaoDeStatusInvalidaError(Exception):
    """A mudanca de status pedida nao e uma aresta valida da maquina
    de estados (secao 5.7)."""
