import { httpClient } from "./httpClient";
import { paramsParaQuery } from "./queryString";
import type { Agendamento, Pagina, StatusAgendamento } from "./types";

export interface ListarAgendamentosParams {
  pagina?: number;
  tamanho_pagina?: number;
  status_filtro?: StatusAgendamento;
  dia?: string; // "AAAA-MM-DD"
  cliente?: string;
}

export interface CriarAgendamentoDados {
  cliente_id: number;
  servico_id: number;
  inicio: string;
  fim: string;
}

export interface RemarcarAgendamentoDados {
  inicio: string;
  fim: string;
}

// Espelha backend/app/rotas/agendamentos.py (Etapas 5, 6 e 7).
export const agendamentosApi = {
  listar: (params: ListarAgendamentosParams = {}) =>
    httpClient.get<Pagina<Agendamento>>(`/agendamentos${paramsParaQuery(params)}`),

  criar: (dados: CriarAgendamentoDados) =>
    httpClient.post<Agendamento>("/agendamentos", dados),

  remarcar: (id: number, dados: RemarcarAgendamentoDados) =>
    httpClient.patch<Agendamento>(`/agendamentos/${id}`, dados),

  mudarStatus: (id: number, status: StatusAgendamento) =>
    httpClient.patch<Agendamento>(`/agendamentos/${id}/status`, { status }),
};
