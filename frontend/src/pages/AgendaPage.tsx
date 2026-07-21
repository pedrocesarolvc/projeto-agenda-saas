// A tela central do projeto (Etapa 7, secao 7.3): "o melhor print do
// portfolio inteiro". Blocos no tempo, cor por status, marcar
// clicando num espaco livre, remarcar arrastando o bloco -- visual
// em vez de formulario cru.

import { useCallback, useState } from "react";
import interactionPlugin from "@fullcalendar/interaction";
import type { DateClickArg, EventResizeDoneArg } from "@fullcalendar/interaction";
import ptBrLocale from "@fullcalendar/core/locales/pt-br";
import type { EventClickArg, EventDropArg } from "@fullcalendar/core";
import FullCalendar from "@fullcalendar/react";
import timeGridPlugin from "@fullcalendar/timegrid";
import { toast } from "sonner";
import { agendamentosApi } from "@/api/agendamentos";
import { ApiError } from "@/api/httpClient";
import type { Agendamento } from "@/api/types";
import AgendamentoDetalhesDialog from "@/components/agenda/AgendamentoDetalhesDialog";
import NovoAgendamentoDialog from "@/components/agenda/NovoAgendamentoDialog";
import { CORES_STATUS } from "@/lib/statusAgendamento";

export default function AgendaPage() {
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([]);
  const [horarioParaCriar, setHorarioParaCriar] = useState<Date | null>(null);
  const [dialogCriarAberto, setDialogCriarAberto] = useState(false);
  const [agendamentoSelecionado, setAgendamentoSelecionado] = useState<Agendamento | null>(null);

  const carregarAgendamentos = useCallback(async () => {
    // O backend nao tem filtro por intervalo de datas (so "dia"
    // exato, Etapa 6) -- para a visao de semana, buscamos ate o teto
    // de paginacao (100, secao 6.3) ordenado por inicio, que cobre
    // sobra o suficiente para o uso real de um v1. Uma agenda que
    // cresça além disso é exatamente o tipo de caso que pede
    // paginação por cursor (roadmap, seção 6.3).
    const pagina = await agendamentosApi.listar({ tamanho_pagina: 100 });
    setAgendamentos(pagina.itens);
  }, []);

  function aoClicarEmData(info: DateClickArg) {
    setHorarioParaCriar(info.date);
    setDialogCriarAberto(true);
  }

  function aoClicarEmEvento(info: EventClickArg) {
    const agendamento = agendamentos.find((item) => String(item.id) === info.event.id);
    if (agendamento) setAgendamentoSelecionado(agendamento);
  }

  async function aoArrastarOuRedimensionar(info: EventDropArg | EventResizeDoneArg) {
    try {
      await agendamentosApi.remarcar(Number(info.event.id), {
        inicio: info.event.start!.toISOString(),
        fim: info.event.end!.toISOString(),
      });
      toast.success("Agendamento remarcado.");
      carregarAgendamentos();
    } catch (excecao) {
      // Etapa 7, secao 7.4: mesma mensagem humana do 409, e o bloco
      // volta pro lugar (revert) -- a interface nao fica com um
      // estado que o backend recusou.
      if (excecao instanceof ApiError && excecao.status === 409) {
        toast.error("Esse horario acabou de ser reservado. Escolha outro.");
      } else {
        toast.error("Nao foi possivel remarcar esse agendamento.");
      }
      info.revert();
    }
  }

  const eventos = agendamentos.map((agendamento) => ({
    id: String(agendamento.id),
    title: `${agendamento.servico_nome} — ${agendamento.cliente_nome}`,
    start: agendamento.inicio,
    end: agendamento.fim,
    backgroundColor: CORES_STATUS[agendamento.status],
    borderColor: CORES_STATUS[agendamento.status],
    editable: agendamento.status === "marcado",
    classNames: agendamento.status === "cancelado" ? ["opacity-50", "line-through"] : [],
  }));

  return (
    <div className="space-y-4">
      <div className="rounded-lg border bg-card p-2 shadow-sm">
        <FullCalendar
          plugins={[timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "timeGridDay,timeGridWeek",
          }}
          locale={ptBrLocale}
          height="auto"
          slotMinTime="07:00:00"
          slotMaxTime="21:00:00"
          allDaySlot={false}
          nowIndicator
          events={eventos}
          dateClick={aoClicarEmData}
          eventClick={aoClicarEmEvento}
          editable
          eventDrop={aoArrastarOuRedimensionar}
          eventResize={aoArrastarOuRedimensionar}
          eventContent={(info) => (
            <div className="overflow-hidden px-1 text-xs leading-tight">
              <p className="truncate font-medium">{info.event.title}</p>
              <p className="truncate opacity-90">{info.timeText}</p>
            </div>
          )}
          datesSet={() => {
            carregarAgendamentos();
          }}
        />
      </div>

      <NovoAgendamentoDialog
        aberto={dialogCriarAberto}
        horarioInicial={horarioParaCriar}
        onFechar={() => setDialogCriarAberto(false)}
        onCriado={() => {
          setDialogCriarAberto(false);
          carregarAgendamentos();
        }}
      />

      <AgendamentoDetalhesDialog
        agendamento={agendamentoSelecionado}
        onFechar={() => setAgendamentoSelecionado(null)}
        onAtualizado={() => {
          setAgendamentoSelecionado(null);
          carregarAgendamentos();
        }}
      />
    </div>
  );
}
