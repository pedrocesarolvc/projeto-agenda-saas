// Criar/editar cliente no mesmo componente (Etapa 6, secao 6.6:
// update parcial -- so os campos preenchidos aqui vao no PUT).

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { clientesApi } from "@/api/clientes";
import { ApiError } from "@/api/httpClient";
import type { Cliente } from "@/api/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Props {
  aberto: boolean;
  clienteExistente: Cliente | null;
  onFechar: () => void;
  onSalvo: () => void;
}

export default function ClienteFormDialog({ aberto, clienteExistente, onFechar, onSalvo }: Props) {
  const [nome, setNome] = useState("");
  const [telefone, setTelefone] = useState("");
  const [email, setEmail] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (!aberto) return;
    setErro(null);
    setNome(clienteExistente?.nome ?? "");
    setTelefone(clienteExistente?.telefone ?? "");
    setEmail(clienteExistente?.email ?? "");
  }, [aberto, clienteExistente]);

  async function aoSubmeter() {
    if (!nome.trim()) {
      setErro("O nome e obrigatorio.");
      return;
    }

    setErro(null);
    setEnviando(true);
    try {
      const dados = { nome, telefone: telefone || undefined, email: email || undefined };
      if (clienteExistente) {
        await clientesApi.atualizar(clienteExistente.id, dados);
        toast.success("Cliente atualizado.");
      } else {
        await clientesApi.criar(dados);
        toast.success("Cliente cadastrado.");
      }
      onSalvo();
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Nao foi possivel salvar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Dialog open={aberto} onOpenChange={(valor) => !valor && onFechar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{clienteExistente ? "Editar cliente" : "Novo cliente"}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nome">Nome</Label>
            <Input id="nome" value={nome} onChange={(e) => setNome(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="telefone">Telefone</Label>
            <Input id="telefone" value={telefone} onChange={(e) => setTelefone(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          {erro && <p className="text-sm text-destructive">{erro}</p>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onFechar} disabled={enviando}>
            Cancelar
          </Button>
          <Button onClick={aoSubmeter} disabled={enviando}>
            {enviando ? "Salvando..." : "Salvar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
