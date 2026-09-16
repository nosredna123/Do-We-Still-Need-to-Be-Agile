import { useState } from "react";
import { chatService } from "@/services/chat.service";
import { useToast } from "@/hooks/use-toast";
import { useChatList } from "./use-chat-list";
import { useMessages } from "./use-messages";

export type { Message } from "./use-messages";

export const useChat = (initialChatId: string | null = null) => {
  const { toast } = useToast();
  const chatList = useChatList(initialChatId);
  const { messages, isChatPending, handleSend, clearMessages, loading: msgLoading, error: msgError } =
    useMessages(chatList.activeId, chatList.setActiveId, chatList.addChat);

  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loading = chatList.loading || msgLoading;
  const error = chatList.error || msgError;

  const handleDelete = (chatId: string) => {
    setDeletingId(chatId);
    chatService
      .deletar(chatId)
      .then(() => {
        chatList.removeChat(chatId);
        clearMessages(chatId);
        toast({ variant: "success", description: "Conversa excluída." });
      })
      .catch(() =>
        toast({
          variant: "error",
          description: "Não foi possível excluir a conversa.",
        }),
      )
      .finally(() => setDeletingId(null));
  };

  return {
    chats: chatList.chats,
    activeId: chatList.activeId,
    messages,
    loading,
    error,
    isChatPending,
    deletingId,
    handleNewChat: chatList.handleNewChat,
    handleSelect: chatList.handleSelect,
    handleDelete,
    handleSend,
  };
};
