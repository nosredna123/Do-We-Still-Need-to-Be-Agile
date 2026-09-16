import { useNavigate } from "react-router-dom";
import { Plus } from "lucide-react";
import NavBar from "@/components/navbar/Navbar";
import ChatCard from "@/components/gallery/ChatCard";
import { useGallery } from "@/hooks/use-gallery";
import { SEVERITY_FILTERS } from "@/lib/verdict";
import { cn } from "@/lib/utils";

const Galeria = () => {
  const navigate = useNavigate();
  const {
    filteredChats,
    loading,
    error,
    filter,
    setFilter,
    deletingId,
    handleDelete,
  } = useGallery();

  return (
    <div className="flex min-h-screen flex-col bg-slate-100 px-4 md:px-16 lg:px-32 xl:px-[12vw]">
      <NavBar variant="app" />

      <main className="mx-auto w-full max-w-6xl flex-1 py-8">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-black">Minha galeria de chats</h1>

          {/* Filtro por severidade. */}
          <div className="flex w-fit items-center gap-1 rounded-lg border border-zinc-300 bg-white p-1 shadow-sm">
            {SEVERITY_FILTERS.map((f) => (
              <button
                key={f.value}
                type="button"
                onClick={() => setFilter(f.value)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm font-semibold transition-colors",
                  filter === f.value
                    ? "bg-foodguard-500 text-white"
                    : "text-slate-600 hover:bg-slate-100",
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-100 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {/* Card de criar nova conversa. */}
          <button
            type="button"
            onClick={() => navigate("/chat")}
            className="flex min-h-[200px] flex-col items-center justify-center gap-3 rounded-xl border border-zinc-300 bg-white text-slate-600 shadow-sm shadow-black/10 transition-all hover:-translate-y-0.5 hover:border-foodguard-500 hover:text-foodguard-600 hover:shadow-md"
          >
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-foodguard-300/60 text-foodguard-600">
              <Plus className="h-6 w-6" strokeWidth={2.5} />
            </span>
            <span className="text-sm font-semibold">Criar nova conversa</span>
          </button>

          {filteredChats.map((chat) => (
            <ChatCard
              key={chat.id}
              chat={chat}
              onOpen={(id) => navigate(`/chat/${id}`)}
              onDelete={handleDelete}
              deleting={deletingId === chat.id}
            />
          ))}
        </div>

        {loading && (
          <p className="mt-8 text-center text-slate-500 animate-pulse">
            Carregando conversas...
          </p>
        )}

        {!loading && filteredChats.length === 0 && (
          <p className="mt-8 text-center text-slate-500">
            {filter === "ALL"
              ? "Você ainda não tem conversas. Crie a primeira!"
              : "Nenhuma conversa nesta categoria de severidade."}
          </p>
        )}
      </main>
    </div>
  );
};

export default Galeria;
