// Tipos espelhando os schemas Pydantic do backend (Etapa 6/7). Cada
// tipo aqui tem um schema correspondente em backend/app/schemas/ --
// se um mudar, o outro precisa mudar junto.

export type Papel = "dono" | "atendente";

export interface UsuarioAtual {
  id: number;
  tenant_id: number;
  papel: Papel;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Tenant {
  id: number;
  nome: string;
}

export interface Cliente {
  id: number;
  nome: string;
  telefone: string | null;
  email: string | null;
}

export interface Servico {
  id: number;
  nome: string;
  duracao_minutos: number;
  // Decimal do Pydantic serializa como string em JSON -- preserva
  // precisao exata (Etapa 6: "dinheiro nao se representa em ponto
  // flutuante binario").
  preco: string;
}

export type StatusAgendamento = "marcado" | "concluido" | "cancelado";

export interface Agendamento {
  id: number;
  cliente_id: number;
  servico_id: number;
  cliente_nome: string;
  servico_nome: string;
  inicio: string;
  fim: string;
  status: StatusAgendamento;
}

// O contrato de paginacao (Etapa 6, secao 6.3): a mesma forma para
// toda listagem, sem excecao.
export interface Pagina<T> {
  itens: T[];
  total: number;
  pagina: number;
  tamanho_pagina: number;
}
