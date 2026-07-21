// A porta de entrada (Etapa 7, secao 7.3): "limpa" -- so email e
// senha, nada de escolher tenant aqui, porque o tenant vem do
// cadastro do usuario (Etapa 3, secao 3.3), nao de uma escolha na
// tela de login.

import { type FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { mensagemDeErro, useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { usuario, carregando, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (!carregando && usuario) {
    const destino = (location.state as { de?: string } | null)?.de ?? "/agenda";
    return <Navigate to={destino} replace />;
  }

  async function aoSubmeter(evento: FormEvent) {
    evento.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await login(email, senha);
      navigate("/agenda", { replace: true });
    } catch (excecao) {
      setErro(mensagemDeErro(excecao));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Entrar</CardTitle>
          <CardDescription>Acesse a agenda do seu negocio.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={aoSubmeter} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(evento) => setEmail(evento.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="senha">Senha</Label>
              <Input
                id="senha"
                type="password"
                autoComplete="current-password"
                required
                value={senha}
                onChange={(evento) => setSenha(evento.target.value)}
              />
            </div>
            {erro && <p className="text-sm text-destructive">{erro}</p>}
            <Button type="submit" className="w-full" disabled={enviando}>
              {enviando ? "Entrando..." : "Entrar"}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            Ainda nao tem uma conta?{" "}
            <Link to="/registrar" className="font-medium text-foreground underline">
              Cadastre seu negocio
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
