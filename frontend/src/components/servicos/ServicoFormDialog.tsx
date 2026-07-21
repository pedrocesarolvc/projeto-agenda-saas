import { useEffect, useState } from "react";
import { toast } from "sonner";
import { ApiError } from "@/api/httpClient";
import { servicosApi } from "@/api/servicos";
import type { Servico } from "@/api/types";
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
  servicoExistente: Servico | null;
  onFechar: () => void;
  onSalvo: () => void;
}

export default function ServicoFormDialog({ aberto, servicoExistente, onFechar, onSalvo }: Props) {
  const [nome, setNome] = useState("");
  const [duracao, setDuracao] = useState("30");
  const [preco, setPreco] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (!aberto) return;
    setErro(null);
    setNome(servicoExistente?.nome ?? "");
    setDuracao(String(servicoExistente?.duracao_minutos ?? 30));
    setPreco(servicoExistente?.preco ?? "");
  }, [aberto, servicoExistente]);

  async function aoSubmeter() {
    setErro(null);
    setEnviando(true);
    try {
      const dados = { nome, duracao_minutos: Number(duracao), preco };
      if (servicoExistente) {
        await servicosApi.atualizar(servicoExistente.id, dados);
        toast.success("Servico atualizado.");
      } else {
        await servicosApi.criar(dados);
        toast.success("Servico cadastrado.");
      }
      onSalvo();
    } catch (excecao) {
      // Etapa 6, secao 6.5: 422 do Pydantic (preco/duracao <= 0) vira
      // uma mensagem no formulario, nao um erro cru.
      if (excecao instanceof ApiError && excecao.camposInvalidos) {
        setErro(Object.values(excecao.camposInvalidos).join(" "));
      } else {
        setErro(excecao instanceof ApiError ? excecao.message : "Nao foi possivel salvar.");
      }
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Dialog open={aberto} onOpenChange={(valor) => !valor && onFechar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{servicoExistente ? "Editar servico" : "Novo servico"}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nome">Nome</Label>
            <Input id="nome" value={nome} onChange={(e) => setNome(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duracao">Duracao (min)</Label>
              <Input
                id="duracao"
                type="number"
                min={1}
                value={duracao}
                onChange={(e) => setDuracao(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="preco">Preco (R$)</Label>
              <Input
                id="preco"
                type="number"
                min={0}
                step="0.01"
                value={preco}
                onChange={(e) => setPreco(e.target.value)}
              />
            </div>
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
