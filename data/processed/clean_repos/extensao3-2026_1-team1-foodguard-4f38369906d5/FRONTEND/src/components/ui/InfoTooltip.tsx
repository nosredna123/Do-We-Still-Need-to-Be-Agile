import { type ReactNode } from "react";
import { Tooltip as TooltipPrimitive } from "radix-ui";
import { HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type InfoTooltipProps = {
  /** Nome acessível do gatilho (lido por leitores de tela). */
  label: string;
  /** Conteúdo exibido no tooltip. */
  children: ReactNode;
  className?: string;
};

/**
 * Ícone de ajuda (?) com tooltip acessível — abre no hover e no foco por
 * teclado. Substitui ícones de ajuda meramente decorativos (A-01).
 */
const InfoTooltip = ({ label, children, className }: InfoTooltipProps) => (
  <TooltipPrimitive.Provider delayDuration={150}>
    <TooltipPrimitive.Root>
      <TooltipPrimitive.Trigger asChild>
        <button
          type="button"
          aria-label={label}
          className={cn(
            "rounded-full text-foodguard-600 transition-colors hover:text-foodguard-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-foodguard-500 focus-visible:ring-offset-2",
            className,
          )}
        >
          <HelpCircle className="h-8 w-8" />
        </button>
      </TooltipPrimitive.Trigger>
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Content
          side="bottom"
          align="start"
          sideOffset={6}
          collisionPadding={12}
          className="z-[100] max-w-xs rounded-lg bg-foodguard-950 px-3 py-2 text-xs leading-relaxed text-white shadow-lg data-[state=delayed-open]:animate-fade-in"
        >
          {children}
          <TooltipPrimitive.Arrow className="fill-foodguard-950" />
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  </TooltipPrimitive.Provider>
);

export default InfoTooltip;
