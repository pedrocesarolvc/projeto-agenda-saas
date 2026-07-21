// Os controles de pagina (Etapa 6, secao 6.3, agora visiveis na tela
// -- "as funcionalidades da Etapa 6 aparecem como controles de
// pagina", Etapa 7 secao 7.3), reutilizados em toda listagem.

import { Button } from "@/components/ui/button";

interface Props {
  pagina: number;
  tamanhoPagina: number;
  total: number;
  onMudarPagina: (pagina: number) => void;
}

export default function PaginacaoControles({ pagina, tamanhoPagina, total, onMudarPagina }: Props) {
  const totalPaginas = Math.max(1, Math.ceil(total / tamanhoPagina));

  return (
    <div className="flex items-center justify-between text-sm text-muted-foreground">
      <span>{total} registro(s)</span>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={pagina <= 1}
          onClick={() => onMudarPagina(pagina - 1)}
        >
          Anterior
        </Button>
        <span>
          Pagina {pagina} de {totalPaginas}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={pagina >= totalPaginas}
          onClick={() => onMudarPagina(pagina + 1)}
        >
          Proxima
        </Button>
      </div>
    </div>
  );
}
