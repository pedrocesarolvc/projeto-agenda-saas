// Configuracao minima do Vite para a interface (Etapa 1, secao 1.6).
//
// Por que React: a propria arquitetura documentada usa "hooks/" como
// nome de pasta (app/hooks/), termo que so faz sentido em React
// (useState, useEffect, hooks customizados). Por isso o frontend
// nasce como um projeto React + Vite.
//
// package.json nao aceita comentario (e JSON puro), entao a
// justificativa de cada dependencia fica registrada aqui:
//   react / react-dom -> a biblioteca de UI em si.
//   vite / @vitejs/plugin-react -> bundler e dev server, rapido para
//     desenvolvimento e o que a maioria dos projetos React usa hoje
//     no lugar do Create React App.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
});
