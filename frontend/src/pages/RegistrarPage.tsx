// Cadastro de negocio (Etapa 7, secao 7.2): cria o tenant e o dono
// numa tela so, e ja deixa logado (POST /auth/registrar-negocio
// devolve token direto).

import { type FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { mensagemDeErro, useAuth } from "@/contexts/AuthContext";

export default function RegistrarPage() {
  const { usuario, carregando, registrarNegocio } = useAuth();
  const navigate = useNavigate();

  const [nomeNegocio, setNomeNegocio] = useState("");
  const [nomeDono, setNomeDono] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (!carregando && usuario) {
    return <Navigate to="/agenda" replace />;
  }

  async function aoSubmeter(evento: FormEvent) {
    evento.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await registrarNegocio({ nome_negocio: nomeNegocio, nome_dono: nomeDono, email, senha });
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
          <CardTitle className="text-2xl">Cadastrar negocio</CardTitle>
          <CardDescription>Crie a conta do seu negocio e comece a agendar.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={aoSubmeter} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nome-negocio">Nome do negocio</Label>
              <Input
                id="nome-negocio"
                placeholder="Barbearia do Ze"
                required
                value={nomeNegocio}
                onChange={(evento) => setNomeNegocio(evento.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="nome-dono">Seu nome</Label>
              <Input
                id="nome-dono"
                required
                value={nomeDono}
                onChange={(evento) => setNomeDono(evento.target.value)}
              />
            </div>
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
                autoComplete="new-password"
                required
                minLength={6}
                value={senha}
                onChange={(evento) => setSenha(evento.target.value)}
              />
            </div>
            {erro && <p className="text-sm text-destructive">{erro}</p>}
            <Button type="submit" className="w-full" disabled={enviando}>
              {enviando ? "Criando..." : "Criar negocio"}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            Ja tem uma conta?{" "}
            <Link to="/login" className="font-medium text-foreground underline">
              Entrar
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
