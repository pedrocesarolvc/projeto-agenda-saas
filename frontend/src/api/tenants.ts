import { httpClient } from "./httpClient";
import type { Tenant } from "./types";

// Espelha backend/app/rotas/tenants.py (Etapa 7, secao 7.3): so o
// suficiente para a interface saber em qual negocio o usuario esta.
export const tenantsApi = {
  meuNegocio: () => httpClient.get<Tenant>("/tenants/me"),
};
