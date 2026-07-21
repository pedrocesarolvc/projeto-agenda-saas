// O cliente HTTP que fala com o backend (Etapa 1, secao 1.6; Etapa 7,
// secao 7.4). Nasceu na Etapa 1 so com a URL base; agora carrega o
// token (Etapa 3) e traduz os status semanticos da API (Etapa 6) num
// formato que a interface consegue mostrar como mensagem humana.

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Secao 6.5: um 422 do Pydantic vem como lista de erros por campo
// (loc/msg). ApiError.camposInvalidos e essa lista ja mapeada para
// "nome do campo -> mensagem", pronta para destacar o input certo no
// formulario (secao 7.4).
export class ApiError extends Error {
  status: number;
  camposInvalidos?: Record<string, string>;

  constructor(status: number, detail: string, camposInvalidos?: Record<string, string>) {
    super(detail);
    this.status = status;
    this.camposInvalidos = camposInvalidos;
  }
}

// Setter em vez de importar o AuthContext direto aqui -- evitaria um
// import circular (o AuthContext tambem usa o httpClient para
// login/registrar). O AuthProvider chama isto assim que monta.
let obterToken: () => string | null = () => null;
let aoReceber401: () => void = () => {};

export function configurarHttpClient(opcoes: {
  obterToken: () => string | null;
  aoReceber401: () => void;
}) {
  obterToken = opcoes.obterToken;
  aoReceber401 = opcoes.aoReceber401;
}

interface DetalheErroPydantic {
  loc?: (string | number)[];
  msg: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = obterToken();

  const resposta = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (resposta.status === 401) {
    aoReceber401();
  }

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => null);

    if (resposta.status === 422 && Array.isArray(corpo?.detail)) {
      const camposInvalidos: Record<string, string> = {};
      for (const erro of corpo.detail as DetalheErroPydantic[]) {
        const campo = String(erro.loc?.[erro.loc.length - 1] ?? "erro");
        camposInvalidos[campo] = erro.msg;
      }
      throw new ApiError(422, "Dados invalidos", camposInvalidos);
    }

    const detail = typeof corpo?.detail === "string" ? corpo.detail : "Erro inesperado";
    throw new ApiError(resposta.status, detail);
  }

  if (resposta.status === 204) {
    return undefined as T;
  }

  return (await resposta.json()) as T;
}

export const httpClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
