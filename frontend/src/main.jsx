// Entry point da interface (Etapa 1, secao 1.6).
// So monta o React na div#root do index.html.
//
// Por que nao ha src/paginas/ nem src/componentes/ ainda:
// a primeira tela real e o login, e login depende da Etapa 3
// (autenticacao), ainda pendente de documentacao. Criar essas pastas
// vazias agora seria antecipar estrutura sem ter o que colocar nela
// (mesmo principio da secao 1.6: "pasta nasce quando o codigo nasce").
// App.jsx fica como o unico componente ate a primeira pagina existir.

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
