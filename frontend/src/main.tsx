// Entry point da interface (Etapa 1, secao 1.6; Etapa 7).
// Monta o React na div#root do index.html e carrega o Tailwind
// (src/index.css) uma unica vez, no topo da arvore.

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
