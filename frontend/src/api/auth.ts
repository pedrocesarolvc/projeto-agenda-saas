import { httpClient } from "./httpClient";
import type { TokenResponse, UsuarioAtual } from "./types";

export interface RegistrarNegocioDados {
  nome_negocio: string;
  nome_dono: string;
  email: string;
  senha: string;
}

// Espelha backend/app/rotas/auth.py (Etapas 3 e 7).
export const authApi = {
  login: (email: string, senha: string) =>
    httpClient.post<TokenResponse>("/auth/login", { email, senha }),

  registrarNegocio: (dados: RegistrarNegocioDados) =>
    httpClient.post<TokenResponse>("/auth/registrar-negocio", dados),

  me: () => httpClient.get<UsuarioAtual>("/auth/me"),
};
