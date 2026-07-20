// src/api/ — o cliente HTTP que fala com o backend (Etapa 1, secao 1.6).
//
// Diferente de paginas/ e componentes/, este arquivo pode existir
// desde ja: nao depende de nenhuma tela pronta, so precisa saber onde
// o backend esta.
//
// O que falta e o que a Etapa 3 (autenticacao) vai acrescentar aqui:
// anexar o JWT do usuario logado em toda requisicao (ex.: header
// "Authorization: Bearer <token>"). Ate la, este client so centraliza
// a URL base — pra quando isso for adicionado, entrar num lugar so.

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  const resposta = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!resposta.ok) {
    throw new Error(`Erro ${resposta.status} ao chamar ${path}`);
  }

  return resposta.json();
}

export const httpClient = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: "DELETE" }),
};
