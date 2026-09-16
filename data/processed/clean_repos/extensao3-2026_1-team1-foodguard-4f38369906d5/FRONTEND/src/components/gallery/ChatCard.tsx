import { useEffect, useRef, useState } from "react";
import { MoreVertical, Trash2, Loader2, Utensils } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import type { Chat } from "@/models/chat.model";
import type { Verdict } from "@/models/message.model";
import { VERDICT_META } from "@/lib/verdict";
import { cn } from "@/lib/utils";

type ChatCardProps = {
  chat: Chat;
  onOpen: (id: string) => void;
  onDelete: (id: string) => void;
  deleting?: boolean;
};

/** Cor da borda do card conforme a severidade da conversa. */
const RING_BY_VERDICT: Record<Verdict, string> = {
  SAFE: "border-green-300",
  LOW_CONCERN: "border-yellow-300",
  MODERATE_RISK: "border-orange-300",
  HIGH_RISK: "border-red-300",
  INSUFFICIENT_DATA: "border-zinc-300",
};

const formatDate = (iso: string): string => {
  try {
    return format(new Date(iso), "d 'de' MMMM 'de' yyyy", { locale: ptBR });
  } catch {
    return "";
  }
};

const ChatCard = ({ chat, onOpen, onDelete, deleting }: ChatCardProps) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [imgError, setImgError] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Fecha o dropdown ao clicar fora dele.
  useEffect(() => {
    if (!menuOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    const confirmed = window.confirm(
      "Tem certeza que deseja deletar esta conversa? Esta ação não pode ser desfeita.",
    );
    if (!confirmed) return;
    onDelete(chat.id);
    setMenuOpen(false);
  };

  const verdictMeta = chat.severity ? VERDICT_META[chat.severity] : null;

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Abrir conversa: ${chat.title ?? "Nova conversa"}`}
      onClick={() => onOpen(chat.id)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onOpen(chat.id);
        }
      }}
      className={cn(
        "group relative flex cursor-pointer flex-col overflow-hidden rounded-xl border bg-white text-left shadow-sm shadow-black/10 transition-all hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-foodguard-500 focus-visible:ring-offset-2",
        chat.severity ? RING_BY_VERDICT[chat.severity] : "border-zinc-300",
      )}
    >
      {/* Imagem do produto (OpenFoodFacts) ou ícone padrão. */}
      <div className="flex h-32 w-full items-center justify-center bg-slate-100">
        {chat.image_url && !imgError ? (
          <img
            src={chat.image_url}
            alt={chat.title ?? "Produto"}
            className="h-full w-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <Utensils className="h-12 w-12 text-foodguard-500/60" strokeWidth={1.5} />
        )}
      </div>

      {/* Menu de ações (...) sobre o canto superior direito. */}
      <div
        ref={menuRef}
        className="absolute right-2 top-2"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Ações da conversa"
          className="flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-zinc-700 shadow-sm transition-colors hover:bg-white"
        >
          <MoreVertical className="h-4 w-4" />
        </button>
        {menuOpen && (
          <div className="absolute right-0 top-full mt-1 rounded-lg border border-gray-200 bg-white shadow-lg">
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleting}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {deleting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              Deletar
            </button>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-3">
        {verdictMeta && (
          <span
            className={cn(
              "inline-flex w-fit items-center rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide",
              verdictMeta.className,
            )}
          >
            {verdictMeta.label}
          </span>
        )}
        <h3 className="line-clamp-2 text-sm font-semibold text-black">
          {chat.title ?? "Nova conversa"}
        </h3>
        <span className="mt-auto text-xs text-slate-500">
          {formatDate(chat.created_at)}
        </span>
      </div>
    </div>
  );
};

export default ChatCard;
