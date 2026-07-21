import { httpClient } from "./httpClient";
import { paramsParaQuery } from "./queryString";
import type { Cliente, Pagina } from "./types";

export interface ListarClientesParams {
  pagina?: number;
  tamanho_pagina?: number;
  busca?: string;
}

export interface ClienteDados {
  nome: string;
  telefone?: string;
  email?: string;
}

// Espelha backend/app/rotas/clientes.py (Etapa 6).
export const clientesApi = {
  listar: (params: ListarClientesParams = {}) =>
    httpClient.get<Pagina<Cliente>>(`/clientes${paramsParaQuery(params)}`),

  criar: (dados: ClienteDados) => httpClient.post<Cliente>("/clientes", dados),

  atualizar: (id: number, dados: Partial<ClienteDados>) =>
    httpClient.put<Cliente>(`/clientes/${id}`, dados),

  remover: (id: number) => httpClient.delete<void>(`/clientes/${id}`),
};
