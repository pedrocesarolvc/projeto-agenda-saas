// O layout autenticado (Etapa 7, secao 7.3): barra superior com o
// nome do negocio atual sempre visivel ("o tenant nao e invisivel, e
// parte da experiencia"), navegacao entre as telas, e o item
// "Servicos" some da navegacao para quem nao e dono -- a permissao
// refletida na interface, com a ressalva da Etapa 3 (secao 3.5):
// isto e conveniencia, a seguranca de verdade ja esta no backend
// (exigir_papel nas rotas de escrita de /servicos).

import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { LogOut, User } from "lucide-react";
import { tenantsApi } from "@/api/tenants";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";

const LINKS = [
  { para: "/agenda", rotulo: "Agenda" },
  { para: "/clientes", rotulo: "Clientes" },
  { para: "/servicos", rotulo: "Servicos", somenteDono: true },
];

export default function Layout() {
  const { usuario, logout } = useAuth();
  const [nomeNegocio, setNomeNegocio] = useState<string | null>(null);

  useEffect(() => {
    tenantsApi
      .meuNegocio()
      .then((tenant) => setNomeNegocio(tenant.nome))
      .catch(() => setNomeNegocio(null));
  }, []);

  const linksVisiveis = LINKS.filter((link) => !link.somenteDono || usuario?.papel === "dono");

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <span className="font-semibold">{nomeNegocio ?? "Carregando..."}</span>
            <nav className="flex gap-1">
              {linksVisiveis.map((link) => (
                <NavLink
                  key={link.para}
                  to={link.para}
                  className={({ isActive }) =>
                    cn(
                      "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-secondary text-secondary-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )
                  }
                >
                  {link.rotulo}
                </NavLink>
              ))}
            </nav>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <User className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel className="capitalize">{usuario?.papel}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout}>
                <LogOut className="mr-2 h-4 w-4" />
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 p-4">
        <Outlet />
      </main>
    </div>
  );
}
