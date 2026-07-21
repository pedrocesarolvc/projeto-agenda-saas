// O formulario de marcar um horario (Etapa 7, secao 7.3): aberto ao
// clicar num espaco livre do calendario -- "marcar um horario sendo
// visual, nao um formulario cru" comeca aqui, mesmo sendo um dialog
// com campos: o PONTO DE PARTIDA ja e o horario clicado, nao uma
// tela em branco.

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { clientesApi } from "@/api/clientes";
import { ApiError } from "@/api/httpClient";
import { agendamentosApi } from "@/api/agendamentos";
import { servicosApi } from "@/api/servicos";
import type { Cliente, Servico } from "@/api/types";
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

// select nativo, nao o Select do shadcn/Radix: um Radix Select
// dentro de um Radix Dialog tem um conflito conhecido de foco/portal
// (o clique na opcao nao chega a registrar, porque o Dialog trata o
// clique no portal do Select como "fora" dele). select nativo nao
// tem esse problema e continua com a mesma aparencia via className.
const classesSelect =
  "h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 md:text-sm dark:bg-input/30";

function paraCampoData(data: Date): string {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, "0");
  const dia = String(data.getDate()).padStart(2, "0");
  return `${ano}-${mes}-${dia}`;
}

function paraCampoHora(data: Date): string {
  const hora = String(data.getHours()).padStart(2, "0");
  const minuto = String(data.getMinutes()).padStart(2, "0");
  return `${hora}:${minuto}`;
}

interface Props {
  aberto: boolean;
  horarioInicial: Date | null;
  onFechar: () => void;
  onCriado: () => void;
}

export default function NovoAgendamentoDialog({
  aberto,
  horarioInicial,
  onFechar,
  onCriado,
}: Props) {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [clienteId, setClienteId] = useState("");
  const [servicoId, setServicoId] = useState("");
  const [data, setData] = useState("");
  const [hora, setHora] = useState("");
  const [duracaoMinutos, setDuracaoMinutos] = useState(30);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (!aberto) return;

    setErro(null);
    setClienteId("");
    setServicoId("");
    setDuracaoMinutos(30);
    const referencia = horarioInicial ?? new Date();
    setData(paraCampoData(referencia));
    setHora(paraCampoHora(referencia));

    // Ate 100 registros (o teto da Etapa 6) bastam para popular um
    // seletor -- listas maiores que isso sao um problema de UX de
    // combobox/busca, nao deste dialog (fica para o v2).
    clientesApi.listar({ tamanho_pagina: 100 }).then((pagina) => setClientes(pagina.itens));
    servicosApi.listar({ tamanho_pagina: 100 }).then((pagina) => setServicos(pagina.itens));
  }, [aberto, horarioInicial]);

  function aoEscolherServico(id: string) {
    setServicoId(id);
    const servico = servicos.find((s) => String(s.id) === id);
    if (servico) setDuracaoMinutos(servico.duracao_minutos);
  }

  async function aoSubmeter() {
    if (!clienteId || !servicoId || !data || !hora) {
      setErro("Preencha cliente, servico, data e horario.");
      return;
    }

    const inicio = new Date(`${data}T${hora}`);
    const fim = new Date(inicio.getTime() + duracaoMinutos * 60_000);

    setErro(null);
    setEnviando(true);
    try {
      await agendamentosApi.criar({
        cliente_id: Number(clienteId),
        servico_id: Number(servicoId),
        inicio: inicio.toISOString(),
        fim: fim.toISOString(),
      });
      toast.success("Agendamento marcado.");
      onCriado();
    } catch (excecao) {
      if (excecao instanceof ApiError && excecao.status === 409) {
        // Etapa 7, secao 7.4: o 409 da race condition da Etapa 5,
        // virando uma frase que faz sentido para quem esta marcando.
        setErro("Esse horario acabou de ser reservado. Escolha outro.");
      } else if (excecao instanceof ApiError && excecao.status === 404) {
        setErro("Cliente ou servico nao encontrado.");
      } else {
        setErro("Nao foi possivel marcar o agendamento. Tente novamente.");
      }
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Dialog open={aberto} onOpenChange={(valor) => !valor && onFechar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Marcar horario</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cliente">Cliente</Label>
            <select
              id="cliente"
              className={classesSelect}
              value={clienteId}
              onChange={(e) => setClienteId(e.target.value)}
            >
              <option value="">Escolha o cliente</option>
              {clientes.map((cliente) => (
                <option key={cliente.id} value={cliente.id}>
                  {cliente.nome}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="servico">Servico</Label>
            <select
              id="servico"
              className={classesSelect}
              value={servicoId}
              onChange={(e) => aoEscolherServico(e.target.value)}
            >
              <option value="">Escolha o servico</option>
              {servicos.map((servico) => (
                <option key={servico.id} value={servico.id}>
                  {servico.nome} ({servico.duracao_minutos} min)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data">Data</Label>
              <Input id="data" type="date" value={data} onChange={(e) => setData(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="hora">Horario</Label>
              <Input id="hora" type="time" value={hora} onChange={(e) => setHora(e.target.value)} />
            </div>
          </div>

          {servicoId && (
            <p className="text-sm text-muted-foreground">Duracao: {duracaoMinutos} minutos.</p>
          )}

          {erro && <p className="text-sm text-destructive">{erro}</p>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onFechar} disabled={enviando}>
            Cancelar
          </Button>
          <Button onClick={aoSubmeter} disabled={enviando}>
            {enviando ? "Marcando..." : "Marcar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
