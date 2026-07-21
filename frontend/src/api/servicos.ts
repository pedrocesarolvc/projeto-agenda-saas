import { httpClient } from "./httpClient";
import { paramsParaQuery } from "./queryString";
import type { Pagina, Servico } from "./types";

export interface ListarServicosParams {
  pagina?: number;
  tamanho_pagina?: number;
}

export interface ServicoDados {
  nome: string;
  duracao_minutos: number;
  preco: string;
}

// Espelha backend/app/rotas/servicos.py (Etapa 6). Criar/editar/
// remover exige papel "dono" no BACKEND (exigir_papel, Etapa 3,
// secao 3.5) -- a interface (Etapa 7, secao 7.3) so esconde os
// controles do atendente por conveniencia; a seguranca real ja
// esta na rota, nao aqui.
export const servicosApi = {
  listar: (params: ListarServicosParams = {}) =>
    httpClient.get<Pagina<Servico>>(`/servicos${paramsParaQuery(params)}`),

  criar: (dados: ServicoDados) => httpClient.post<Servico>("/servicos", dados),

  atualizar: (id: number, dados: Partial<ServicoDados>) =>
    httpClient.put<Servico>(`/servicos/${id}`, dados),

  remover: (id: number) => httpClient.delete<void>(`/servicos/${id}`),
};
