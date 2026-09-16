import { useContext } from "react";
import { ToastContext } from "@/context/ToastContext";

/** Acesso ao disparador de toasts. Deve estar sob `<ToastProvider>`. */
export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast deve ser usado dentro de <ToastProvider>.");
  }
  return ctx;
};
