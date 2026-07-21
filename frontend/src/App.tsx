// O roteador (Etapa 7): publicas (login/registrar) e protegidas
// (agenda/clientes/servicos, atras de RotaProtegida -- redireciona
// para /login se nao houver usuario autenticado).

import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import Layout from "@/components/Layout";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import AgendaPage from "@/pages/AgendaPage";
import ClientesPage from "@/pages/ClientesPage";
import LoginPage from "@/pages/LoginPage";
import RegistrarPage from "@/pages/RegistrarPage";
import ServicosPage from "@/pages/ServicosPage";

function RotaProtegida({ children }: { children: ReactNode }) {
  const { usuario, carregando } = useAuth();
  const location = useLocation();

  if (carregando) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Carregando...
      </div>
    );
  }

  if (!usuario) {
    return <Navigate to="/login" replace state={{ de: location.pathname }} />;
  }

  return <>{children}</>;
}

function Rotas() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registrar" element={<RegistrarPage />} />
      <Route
        path="/"
        element={
          <RotaProtegida>
            <Layout />
          </RotaProtegida>
        }
      >
        <Route index element={<Navigate to="/agenda" replace />} />
        <Route path="agenda" element={<AgendaPage />} />
        <Route path="clientes" element={<ClientesPage />} />
        <Route path="servicos" element={<ServicosPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Rotas />
        <Toaster />
      </AuthProvider>
    </BrowserRouter>
  );
}
