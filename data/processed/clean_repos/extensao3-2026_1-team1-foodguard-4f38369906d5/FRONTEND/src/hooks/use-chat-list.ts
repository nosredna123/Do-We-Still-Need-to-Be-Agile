import { useCallback, useEffect, useState } from "react";
import type { Chat } from "@/models/chat.model";
import { chatService } from "@/services/chat.service";
import { ANAMNESE_UPDATED_EVENT } from "@/lib/events";

export const useChatList = (initialActiveId: string | null = null) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeId, setActiveId] = useState<string | null>(initialActiveId);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadChats = useCallback(() => {
    setLoading(true);
    chatService
      .listar()
      .then((data) => setChats(data))
      .catch(() => setError("Erro ao carregar conversas."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // Carregamento inicial da lista de conversas (data fetching no mount).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadChats();
  }, [loadChats]);

  // RN004: ao atualizar a anamnese, os chats antigos são invalidados no backend.
  // Recarregamos a lista e limpamos o chat ativo para não exibir um chat obsoleto.
  useEffect(() => {
    const handleAnamneseUpdated = () => {
      setActiveId(null);
      loadChats();
    };
    window.addEventListener(ANAMNESE_UPDATED_EVENT, handleAnamneseUpdated);
    return () =>
      window.removeEventListener(ANAMNESE_UPDATED_EVENT, handleAnamneseUpdated);
  }, [loadChats]);

  const handleNewChat = () => setActiveId(null);

  const handleSelect = (id: string) => {
    setError(null);
    setActiveId(id);
  };

  const addChat = (chat: Chat) => setChats((prev) => [chat, ...prev]);

  const removeChat = (chatId: string) => {
    setChats((prev) => prev.filter((c) => c.id !== chatId));
    if (activeId === chatId) setActiveId(null);
  };

  return {
    chats,
    activeId,
    setActiveId,
    loading,
    error,
    setError,
    handleNewChat,
    handleSelect,
    addChat,
    removeChat,
  };
};
