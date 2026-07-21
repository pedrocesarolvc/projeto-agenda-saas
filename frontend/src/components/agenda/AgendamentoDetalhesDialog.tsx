// Clicar num bloco existente do calendario abre isto: os detalhes e
// as acoes que a maquina de estados da Etapa 5 permite dali (secao
// 5.7) -- so os botoes validos para o status atual aparecem.

import { useState } from "react";
import { toast } from "sonner";
import { agendamentosApi } from "@/api/agendamentos";
import { ApiError } from "@/api/httpClient";
import type { Agendamento, StatusAgendamento } from "@/api/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ROTULOS_STATUS, TRANSICOES_VALIDAS } from "@/lib/statusAgendamento";

interface Props {
  agendamento: Agendamento | null;
  onFechar: () => void;
  onAtualizado: () => void;
}

const FORMATADOR_HORARIO = new Intl.DateTimeFormat("pt-BR", {
  weekday: "short",
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

export default function AgendamentoDetalhesDialog({ agendamento, onFechar, onAtualizado }: Props) {
  const [enviando, setEnviando] = useState(false);

  if (!agendamento) return null;

  async function mudarPara(novoStatus: StatusAgendamento) {
    setEnviando(true);
    try {
      await agendamentosApi.mudarStatus(agendamento!.id, novoStatus);
      toast.success(`Agendamento marcado como ${ROTULOS_STATUS[novoStatus].toLowerCase()}.`);
      onAtualizado();
    } catch (excecao) {
      const mensagem =
        excecao instanceof ApiError ? excecao.message : "Nao foi possivel atualizar o status.";
      toast.error(mensagem);
    } finally {
      setEnviando(false);
    }
  }

  const transicoes = TRANSICOES_VALIDAS[agendamento.status];

  return (
    <Dialog open={!!agendamento} onOpenChange={(valor) => !valor && onFechar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{agendamento.servico_nome}</DialogTitle>
        </DialogHeader>

        <div className="space-y-3">
          <p className="text-sm">
            <span className="text-muted-foreground">Cliente: </span>
            {agendamento.cliente_nome}
          </p>
          <p className="text-sm">
            <span className="text-muted-foreground">Horario: </span>
            {FORMATADOR_HORARIO.format(new Date(agendamento.inicio))} —{" "}
            {FORMATADOR_HORARIO.format(new Date(agendamento.fim))}
          </p>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Status:</span>
            <Badge variant="outline">{ROTULOS_STATUS[agendamento.status]}</Badge>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onFechar} disabled={enviando}>
            Fechar
          </Button>
          {transicoes.includes("cancelado") && (
            <Button variant="destructive" onClick={() => mudarPara("cancelado")} disabled={enviando}>
              Cancelar agendamento
            </Button>
          )}
          {transicoes.includes("concluido") && (
            <Button onClick={() => mudarPara("concluido")} disabled={enviando}>
              Marcar como concluido
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
