import type { StatusAgendamento } from "@/api/types";

// Cor por status (Etapa 7, secao 7.3) -- as variaveis vem de
// src/index.css, um lugar so para o calendario e os badges lerem a
// mesma paleta.
export const CORES_STATUS: Record<StatusAgendamento, string> = {
  marcado: "var(--status-marcado)",
  concluido: "var(--status-concluido)",
  cancelado: "var(--status-cancelado)",
};

export const ROTULOS_STATUS: Record<StatusAgendamento, string> = {
  marcado: "Marcado",
  concluido: "Concluido",
  cancelado: "Cancelado",
};

// Etapa 5, secao 5.7: a maquina de estados, espelhada aqui so para a
// interface saber quais botoes de acao mostrar -- a validacao de
// verdade continua sendo feita pelo backend a cada chamada.
export const TRANSICOES_VALIDAS: Record<StatusAgendamento, StatusAgendamento[]> = {
  marcado: ["concluido", "cancelado"],
  concluido: [],
  cancelado: [],
};
