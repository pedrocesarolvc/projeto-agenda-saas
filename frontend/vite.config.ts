// Configuracao do Vite (Etapa 1, secao 1.6; Etapa 7, secao 7.3).
//
// @tailwindcss/vite: plugin oficial do Tailwind v4 -- sem postcss.config
// separado, so isto mais o `@import "tailwindcss"` no CSS (src/index.css).
//
// resolve.alias "@/*": o mesmo caminho que tsconfig.json declara, para
// imports como `@/components/ui/button` funcionarem em runtime (Vite)
// e em type-check (TypeScript) ao mesmo tempo -- e o padrao que o
// shadcn/ui espera do projeto.

import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
