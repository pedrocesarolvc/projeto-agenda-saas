// Etapa 7, secao 7.3: "a lista de clientes com busca por nome" --
// as conveniencias da Etapa 6 (busca, paginacao) visiveis na tela,
// nao so no endpoint.

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { clientesApi } from "@/api/clientes";
import { ApiError } from "@/api/httpClient";
import type { Cliente, Pagina } from "@/api/types";
import PaginacaoControles from "@/components/PaginacaoControles";
import ClienteFormDialog from "@/components/clientes/ClienteFormDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const TAMANHO_PAGINA = 10;

export default function ClientesPage() {
  const [dados, setDados] = useState<Pagina<Cliente> | null>(null);
  const [busca, setBusca] = useState("");
  const [pagina, setPagina] = useState(1);
  const [carregando, setCarregando] = useState(true);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [clienteEditando, setClienteEditando] = useState<Cliente | null>(null);

  async function carregar() {
    setCarregando(true);
    try {
      const resposta = await clientesApi.listar({ pagina, tamanho_pagina: TAMANHO_PAGINA, busca });
      setDados(resposta);
    } finally {
      setCarregando(false);
    }
  }

  // Debounce simples: a busca so dispara 300ms depois que o usuario
  // para de digitar, senao cada tecla vira uma requisicao.
  useEffect(() => {
    const temporizador = setTimeout(() => {
      setPagina(1);
      carregar();
    }, 300);
    return () => clearTimeout(temporizador);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busca]);

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagina]);

  function abrirNovo() {
    setClienteEditando(null);
    setDialogAberto(true);
  }

  function abrirEdicao(cliente: Cliente) {
    setClienteEditando(cliente);
    setDialogAberto(true);
  }

  async function remover(cliente: Cliente) {
    if (!window.confirm(`Remover ${cliente.nome}?`)) return;
    try {
      await clientesApi.remover(cliente.id);
      toast.success("Cliente removido.");
      carregar();
    } catch (excecao) {
      toast.error(excecao instanceof ApiError ? excecao.message : "Nao foi possivel remover.");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <Input
          placeholder="Buscar por nome..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="max-w-sm"
        />
        <Button onClick={abrirNovo}>
          <Plus className="mr-2 h-4 w-4" />
          Novo cliente
        </Button>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Telefone</TableHead>
              <TableHead>E-mail</TableHead>
              <TableHead className="w-24 text-right">Acoes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {!carregando && dados?.itens.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  Nenhum cliente encontrado.
                </TableCell>
              </TableRow>
            )}
            {dados?.itens.map((cliente) => (
              <TableRow key={cliente.id}>
                <TableCell className="font-medium">{cliente.nome}</TableCell>
                <TableCell>{cliente.telefone ?? "—"}</TableCell>
                <TableCell>{cliente.email ?? "—"}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" onClick={() => abrirEdicao(cliente)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => remover(cliente)}>
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

      <ClienteFormDialog
        aberto={dialogAberto}
        clienteExistente={clienteEditando}
        onFechar={() => setDialogAberto(false)}
        onSalvo={() => {
          setDialogAberto(false);
          carregar();
        }}
      />
    </div>
  );
}
