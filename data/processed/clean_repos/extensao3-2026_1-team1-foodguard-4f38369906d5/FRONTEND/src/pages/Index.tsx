import { useMemo, useState } from "react";
import NavBar from "@/components/navbar/Navbar";
import Sidebar from "@/components/sideBar/SideBar";
import ChatInput from "@/components/chatInput/ChatInput";
import ChatMessages from "@/components/chatMessages/ChatMessages";
import EmptyChat from "@/components/emptyChat/EmptyChat";
import { useChat } from "@/hooks/use-chat";

type IndexProps = {
  /** Conversa aberta a partir da galeria (rota /chat/:chatId). */
  initialChatId?: string | null;
};

const Index = ({ initialChatId = null }: IndexProps) => {
  // Sidebar fechada por padrão em telas < md (768px).
  const [sidebarOpen, setSidebarOpen] = useState(
    () => typeof window !== "undefined" && window.innerWidth >= 768,
  );
  const {
    chats,
    activeId,
    messages,
    loading,
    error,
    isChatPending,
    deletingId,
    handleNewChat,
    handleSelect,
    handleDelete,
    handleSend,
  } = useChat(initialChatId);

  const conversations = useMemo(
    () =>
      chats.map((c) => ({
        id: c.id,
        title: c.title ?? "Nova conversa",
      })),
    [chats],
  );

  // Chat selecionado foi fechado (anamnese atualizada) → só leitura.
  const isChatClosed = useMemo(
    () => chats.some((c) => c.id === activeId && c.is_open === false),
    [chats, activeId],
  );

  return (
    <div className="flex px-4 md:px-16 lg:px-32 xl:px-[15vw] h-screen flex-col bg-slate-100 overflow-hidden">
      <NavBar variant="app" />

      <main className="mx-auto flex w-full max-w-6xl flex-1 gap-8 px-6 py-8 overflow-hidden">
        <Sidebar
          open={sidebarOpen}
          onToggle={() => setSidebarOpen((v) => !v)}
          onNewChat={handleNewChat}
          conversations={conversations}
          activeId={activeId}
          onSelect={handleSelect}
          onDelete={handleDelete}
          deletingId={deletingId}
        />

        <section className="flex flex-1 flex-col overflow-hidden">
          {error && (
            <div className="mb-2 rounded-lg bg-red-100 px-4 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="flex flex-1 flex-col overflow-y-auto">
            {loading && messages.length === 0 ? (
              <div className="flex flex-1 items-center justify-center">
                <span className="text-slate-500 animate-pulse">
                  Carregando...
                </span>
              </div>
            ) : messages.length === 0 ? (
              <EmptyChat />
            ) : (
              <ChatMessages messages={messages} />
            )}
          </div>

          <div className="pt-4 shrink-0">
            {isChatClosed ? (
              <div className="flex flex-col items-center gap-2 rounded-3xl border border-zinc-400 bg-slate-50 px-6 py-4 text-center">
                <p className="text-sm font-medium text-slate-600">
                  Esta conversa foi encerrada após a atualização da sua anamnese e está
                  disponível apenas para leitura.
                </p>
                <button
                  type="button"
                  onClick={handleNewChat}
                  className="rounded-lg bg-foodguard-500 px-5 py-2 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-500/90"
                >
                  Nova conversa
                </button>
              </div>
            ) : (
              <ChatInput onSend={handleSend} disabled={isChatPending} />
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Index;
