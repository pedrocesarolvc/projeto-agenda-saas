// O contexto de autenticacao (Etapa 3 no frontend; Etapa 7, secao
// 7.3: "a interface sempre deixa claro em qual negocio o usuario
// esta"). Guarda o token (localStorage, sobrevive a um refresh) e o
// usuario atual (id/tenant_id/papel, vindo de GET /auth/me).
//
// O ponto de design que espelha o backend: o papel e o tenant_id
// aqui vem SEMPRE do que o servidor devolveu a partir do token, nunca
// de algo que o proprio frontend inventou -- o mesmo principio da
// Etapa 3, secao 3.4, do lado do cliente.

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { authApi, type RegistrarNegocioDados } from "@/api/auth";
import { ApiError, configurarHttpClient } from "@/api/httpClient";
import type { UsuarioAtual } from "@/api/types";

interface AuthContextValue {
  usuario: UsuarioAtual | null;
  carregando: boolean;
  login: (email: string, senha: string) => Promise<void>;
  registrarNegocio: (dados: RegistrarNegocioDados) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const CHAVE_TOKEN = "agenda:token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(CHAVE_TOKEN));
  const [usuario, setUsuario] = useState<UsuarioAtual | null>(null);
  const [carregando, setCarregando] = useState(true);

  // Registra no httpClient como ele pega o token e o que fazer num
  // 401 -- feito aqui, nao no httpClient, pra evitar import circular
  // (httpClient nao conhece o AuthContext; o AuthContext e quem
  // configura o httpClient).
  useEffect(() => {
    configurarHttpClient({
      obterToken: () => token,
      aoReceber401: () => {
        setToken(null);
        setUsuario(null);
        localStorage.removeItem(CHAVE_TOKEN);
      },
    });
  }, [token]);

  useEffect(() => {
    if (!token) {
      setUsuario(null);
      setCarregando(false);
      return;
    }
    setCarregando(true);
    authApi
      .me()
      .then(setUsuario)
      .catch(() => {
        localStorage.removeItem(CHAVE_TOKEN);
        setToken(null);
      })
      .finally(() => setCarregando(false));
  }, [token]);

  const login = async (email: string, senha: string) => {
    const resposta = await authApi.login(email, senha);
    localStorage.setItem(CHAVE_TOKEN, resposta.access_token);
    setToken(resposta.access_token);
  };

  const registrarNegocio = async (dados: RegistrarNegocioDados) => {
    const resposta = await authApi.registrarNegocio(dados);
    localStorage.setItem(CHAVE_TOKEN, resposta.access_token);
    setToken(resposta.access_token);
  };

  const logout = () => {
    localStorage.removeItem(CHAVE_TOKEN);
    setToken(null);
    setUsuario(null);
  };

  const value = useMemo(
    () => ({ usuario, carregando, login, registrarNegocio, logout }),
    [usuario, carregando]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const contexto = useContext(AuthContext);
  if (!contexto) {
    throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  }
  return contexto;
}

// Traduz o ApiError num texto que uma tela de formulario pode
// mostrar direto -- usado por Login/Registrar (Etapa 7, secao 7.4).
export function mensagemDeErro(erro: unknown): string {
  if (erro instanceof ApiError) return erro.message;
  return "Erro inesperado. Tente novamente.";
}
