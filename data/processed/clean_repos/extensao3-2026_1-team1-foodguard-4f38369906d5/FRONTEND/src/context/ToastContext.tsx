import {
  createContext,
  useCallback,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { Toast as ToastPrimitive } from "radix-ui";
import { X, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastVariant = "default" | "success" | "error";

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface ToastOptions {
  title?: string;
  description: string;
  variant?: ToastVariant;
  action?: ToastAction;
  duration?: number;
}

interface ToastItem extends ToastOptions {
  id: string;
}

interface ToastContextValue {
  /** Dispara um toast; retorna o id criado. */
  toast: (options: ToastOptions) => string;
}

// eslint-disable-next-line react-refresh/only-export-components
export const ToastContext = createContext<ToastContextValue | null>(null);

const VARIANT_META: Record<
  ToastVariant,
  { icon: typeof Info; accent: string; border: string }
> = {
  default: { icon: Info, accent: "text-foodguard-600", border: "border-zinc-300" },
  success: {
    icon: CheckCircle2,
    accent: "text-foodguard-600",
    border: "border-foodguard-300",
  },
  error: { icon: AlertCircle, accent: "text-red-600", border: "border-red-300" },
};

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const counterRef = useRef(0);

  const remove = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((options: ToastOptions) => {
    const id = `toast-${counterRef.current++}`;
    setToasts((prev) => [
      ...prev,
      { id, variant: "default", duration: 5000, ...options },
    ]);
    return id;
  }, []);

  const value = useMemo<ToastContextValue>(() => ({ toast }), [toast]);

  return (
    <ToastContext.Provider value={value}>
      <ToastPrimitive.Provider swipeDirection="right">
        {children}

        {toasts.map((t) => {
          const meta = VARIANT_META[t.variant ?? "default"];
          const Icon = meta.icon;
          return (
            <ToastPrimitive.Root
              key={t.id}
              duration={t.duration}
              onOpenChange={(open) => {
                if (!open) remove(t.id);
              }}
              className={cn(
                "flex items-start gap-3 rounded-lg border bg-white p-4 shadow-lg shadow-black/10",
                "data-[state=open]:animate-fade-in data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=cancel]:translate-x-0 data-[swipe=cancel]:transition-transform",
                meta.border,
              )}
            >
              <Icon className={cn("mt-0.5 h-5 w-5 shrink-0", meta.accent)} />
              <div className="flex-1">
                {t.title && (
                  <ToastPrimitive.Title className="text-sm font-bold text-black">
                    {t.title}
                  </ToastPrimitive.Title>
                )}
                <ToastPrimitive.Description className="text-sm text-slate-700">
                  {t.description}
                </ToastPrimitive.Description>
              </div>
              {t.action && (
                <ToastPrimitive.Action altText={t.action.label} asChild>
                  <button
                    onClick={t.action.onClick}
                    className="shrink-0 rounded-md px-2 py-1 text-sm font-bold text-foodguard-600 hover:bg-foodguard-50"
                  >
                    {t.action.label}
                  </button>
                </ToastPrimitive.Action>
              )}
              <ToastPrimitive.Close
                aria-label="Fechar"
                className="shrink-0 rounded-md p-1 text-slate-400 transition-colors hover:text-black"
              >
                <X className="h-4 w-4" />
              </ToastPrimitive.Close>
            </ToastPrimitive.Root>
          );
        })}

        <ToastPrimitive.Viewport className="fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col gap-2 p-4 outline-none sm:max-w-sm" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  );
};
