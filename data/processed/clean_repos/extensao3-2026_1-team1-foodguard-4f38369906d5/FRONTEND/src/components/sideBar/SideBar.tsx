import { Menu, SquarePen, MoreVertical, Trash2, Loader2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

export type Conversation = { id: string; title: string };

type SidebarProps = {
  open: boolean;
  onToggle: () => void;
  onNewChat: () => void;
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  deletingId?: string | null;
};

const Sidebar = ({
  open,
  onToggle,
  onNewChat,
  conversations,
  activeId,
  onSelect,
  onDelete,
  deletingId,
}: SidebarProps) => {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Fecha o dropdown ao clicar fora dele.
  useEffect(() => {
    if (!openMenuId) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpenMenuId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [openMenuId]);

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const confirmed = window.confirm(
      "Tem certeza que deseja deletar esta conversa? Esta ação não pode ser desfeita.",
    );
    if (!confirmed) return;
    onDelete(id);
    setOpenMenuId(null);
  };
  return (
    <aside
      className={cn(
        "flex flex-col border border-zinc-500 bg-white p-4 shadow-sm shadow-black/15 transition-all duration-300",
        open ? "w-52 rounded-xl" : "w-16 items-center rounded-lg",
      )}
    >
      <button
        onClick={onToggle}
        aria-label={open ? "Fechar menu" : "Abrir menu"}
        className="flex h-10 w-10 items-center justify-center rounded-lg text-black hover:bg-slate-200"
      >
        <Menu className="h-6 w-6" strokeWidth={2.5} />
      </button>

      <button
        onClick={onNewChat}
        className={cn(
          "mt-4 flex items-center rounded-lg text-black hover:bg-slate-200",
          open ? "w-full gap-3 px-2 py-2" : "h-10 w-10 justify-center",
        )}
        aria-label="Nova conversa"
      >
        <SquarePen className="h-6 w-6 shrink-0" strokeWidth={2.2} />
        {open && (
          <span className="text-base font-medium truncate">Nova conversa</span>
        )}
      </button>

      {open && (
        <div className="mt-6 flex-1 overflow-y-auto">
          <h2 className="mb-3 px-2 text-xl font-bold text-black">Conversas</h2>
          <ul className="space-y-1">
            {conversations.map((c) => {
              const active = c.id === activeId;
              const isOpen = openMenuId === c.id;
              return (
                <li key={c.id}>
                  <div
                    ref={isOpen ? menuRef : undefined}
                    className={cn(
                      "group relative flex w-full cursor-default items-center justify-between rounded-lg px-3 py-2 text-left font-semibold transition-colors",
                      active
                        ? "bg-foodguard-500 text-white"
                        : "text-black hover:bg-slate-200",
                    )}
                  >
                    <button
                      onClick={() => onSelect(c.id)}
                      className="min-w-0 flex-1 truncate text-left"
                    >
                      {c.title}
                    </button>
                    <button
                      onClick={() => setOpenMenuId(isOpen ? null : c.id)}
                      className={cn(
                        "h-4 w-4 shrink-0 opacity-0 transition-opacity",
                        active ? "opacity-100" : "group-hover:opacity-100",
                      )}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                    {isOpen && (
                      <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                        <button
                          onClick={(e) => handleDelete(e, c.id)}
                          disabled={deletingId === c.id}
                          className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg w-full disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {deletingId === c.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                          Deletar
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
