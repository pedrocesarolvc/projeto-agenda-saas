import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// O helper padrao do shadcn/ui: junta classes condicionais (clsx) e
// resolve conflitos de utilitarios Tailwind (twMerge) -- usado por
// todo componente em components/ui/.
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
