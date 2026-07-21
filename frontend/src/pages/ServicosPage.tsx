// Etapa 7, secao 7.3: paginacao visivel mesmo aqui -- "toda listagem
// pagina, sem excecao" (Etapa 6, secao 6.3), inclusive a de servicos
// que "nunca vai ter muitos". Esta tela so e alcancavel por quem e
// dono (Layout esconde o link); o backend tambem exige (Etapa 3,
// secao 3.5) nas rotas de escrita -- as duas metades da seguranca.

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { ApiError } from "@/api/httpClient";
import { servicosApi } from "@/api/servicos";
import type { Pagina, Servico } from "@/api/types";
import PaginacaoControles from "@/components/PaginacaoControles";
import ServicoFormDialog from "@/components/servicos/ServicoFormDialog";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const TAMANHO_PAGINA = 10;

function formatarPreco(preco: string): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
    Number(preco)
  );
}

export default function ServicosPage() {
  const [dados, setDados] = useState<Pagina<Servico> | null>(null);
  const [pagina, setPagina] = useState(1);
  const [carregando, setCarregando] = useState(true);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [servicoEditando, setServicoEditando] = useState<Servico | null>(null);

  async function carregar() {
    setCarregando(true);
    try {
      const resposta = await servicosApi.listar({ pagina, tamanho_pagina: TAMANHO_PAGINA });
      setDados(resposta);
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagina]);

  function abrirNovo() {
    setServicoEditando(null);
    setDialogAberto(true);
  }

  function abrirEdicao(servico: Servico) {
    setServicoEditando(servico);
    setDialogAberto(true);
  }

  async function remover(servico: Servico) {
    if (!window.confirm(`Remover ${servico.nome}?`)) return;
    try {
      await servicosApi.remover(servico.id);
      toast.success("Servico removido.");
      carregar();
    } catch (excecao) {
      toast.error(excecao instanceof ApiError ? excecao.message : "Nao foi possivel remover.");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Servicos</h1>
        <Button onClick={abrirNovo}>
          <Plus className="mr-2 h-4 w-4" />
          Novo servico
        </Button>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Duracao</TableHead>
              <TableHead>Preco</TableHead>
              <TableHead className="w-24 text-right">Acoes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {!carregando && dados?.itens.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  Nenhum servico cadastrado.
                </TableCell>
              </TableRow>
            )}
            {dados?.itens.map((servico) => (
              <TableRow key={servico.id}>
                <TableCell className="font-medium">{servico.nome}</TableCell>
                <TableCell>{servico.duracao_minutos} min</TableCell>
                <TableCell>{formatarPreco(servico.preco)}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" onClick={() => abrirEdicao(servico)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => remover(servico)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {dados && (
        <PaginacaoControles
          pagina={dados.pagina}
          tamanhoPagina={dados.tamanho_pagina}
          total={dados.total}
          onMudarPagina={setPagina}
        />
      )}

      <ServicoFormDialog
        aberto={dialogAberto}
        servicoExistente={servicoEditando}
        onFechar={() => setDialogAberto(false)}
        onSalvo={() => {
          setDialogAberto(false);
          carregar();
        }}
      />
    </div>
  );
}
