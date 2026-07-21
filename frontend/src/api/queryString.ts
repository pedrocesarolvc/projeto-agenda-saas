// Helper compartilhado pelas listagens (clientes, servicos,
// agendamentos): monta a query string so com os parametros
// realmente informados -- o mesmo padrao "so restringe se veio" da
// Etapa 6, secao 6.4, do lado do cliente.
export function paramsParaQuery<T extends object>(params: T): string {
  const query = new URLSearchParams();
  for (const [chave, valor] of Object.entries(params as Record<string, unknown>)) {
    if (valor !== undefined && valor !== null && valor !== "") {
      query.set(chave, String(valor));
    }
  }
  const texto = query.toString();
  return texto ? `?${texto}` : "";
}
