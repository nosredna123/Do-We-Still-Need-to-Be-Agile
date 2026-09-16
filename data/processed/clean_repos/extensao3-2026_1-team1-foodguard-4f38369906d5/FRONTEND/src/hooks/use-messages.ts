import { useEffect, useRef, useState } from "react";
import type { Chat } from "@/models/chat.model";
import { MessageRole } from "@/enums/MessageRole";
import type { Message as BackendMessage, Verdict } from "@/models/message.model";
import type { IOpenFoodProduct } from "@/models/open-food.model";
import { messageService } from "@/services/message.service";

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  image?: File;
  imageUrl?: string;
  pending?: boolean;
  verdict?: Verdict | null;
  recommendsDoctor?: boolean;
}

// Chave temporária de um chat ainda não persistido no backend (não deve gerar fetch).
const NEW_CHAT_KEY = "__new__";

/** Trunca o texto até a 4ª palavra (sem quebrar palavras), com reticências
 * quando houver mais. Espelha o `_chat_title` do backend. */
function truncateTitle(text: string): string {
  const words = text.trim().split(/\s+/).filter(Boolean);
  const title = words.slice(0, 4).join(" ");
  return words.length > 4 ? `${title}...` : title;
}

function mapRole(role: MessageRole): "user" | "assistant" {
  return role === MessageRole.User ? "user" : "assistant";
}

function mapBackendMessages(messages: BackendMessage[]): Message[] {
  return messages.map((m, i) => ({
    id: `${m.created_at}-${i}`,
    role: mapRole(m.role),
    text: m.content,
    verdict: m.verdict,
    recommendsDoctor: m.recommends_doctor,
  }));
}

export const useMessages = (
  activeId: string | null,
  setActiveId: (id: string | null) => void,
  addChat: (chat: Chat) => void,
) => {
  const [messagesByChat, setMessagesByChat] = useState<
    Record<string, Message[]>
  >({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fetchedChatsRef = useRef<Set<string>>(new Set());
  const objectUrlsRef = useRef<Set<string>>(new Set());

  const messages = activeId ? (messagesByChat[activeId] ?? []) : [];
  const isChatPending = messages.some((m) => m.pending);

  useEffect(() => {
    // Não busca para o placeholder de chat novo (ainda não existe no backend).
    if (!activeId || activeId === NEW_CHAT_KEY || fetchedChatsRef.current.has(activeId))
      return;
    fetchedChatsRef.current.add(activeId);

    // Data fetching das mensagens do chat ao trocar de conversa.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    messageService
      .listar(activeId)
      .then((data) => {
        setMessagesByChat((prev) => ({
          ...prev,
          [activeId]: mapBackendMessages(data),
        }));
      })
      .catch(() => {
        fetchedChatsRef.current.delete(activeId);
        setError("Erro ao carregar mensagens.");
      })
      .finally(() => setLoading(false));
  }, [activeId]);

  useEffect(() => {
    const urls = objectUrlsRef.current;
    return () => {
      urls.forEach((url) => URL.revokeObjectURL(url));
      urls.clear();
    };
  }, []);

  const clearMessages = (chatId: string) => {
    fetchedChatsRef.current.delete(chatId);
    setMessagesByChat((prev) => {
      const copy = { ...prev };
      delete copy[chatId];
      return copy;
    });
  };

  const handleSend = (
    text: string,
    image?: File,
    product?: IOpenFoodProduct,
  ) => {
    if (isChatPending) return;

    const productName = product?.product.product_name;

    let finalMessage = text;
    if (productName) {
      if (!text.trim()) {
        finalMessage = `Acabei de escanear o produto: ${productName}. O que você pode me dizer sobre ele?`;
      } else {
        finalMessage = `${text}\n\n[Produto escaneado: ${productName}]`;
      }
    }

    const imageUrl = image ? URL.createObjectURL(image) : undefined;
    if (imageUrl) objectUrlsRef.current.add(imageUrl);

    const userMsg: Message = {
      id: `u${crypto.randomUUID()}`,
      role: "user",
      text: finalMessage,
      image,
      imageUrl,
    };

    const pendingMsg: Message = {
      id: `p${crypto.randomUUID()}`,
      role: "assistant",
      text: "",
      pending: true,
    };

    const currentChatId = activeId;

    setMessagesByChat((prev) => ({
      ...prev,
      [currentChatId ?? NEW_CHAT_KEY]: [
        ...(prev[currentChatId ?? NEW_CHAT_KEY] ?? []),
        userMsg,
        pendingMsg,
      ],
    }));

    if (!currentChatId) {
      setActiveId(NEW_CHAT_KEY);
    }

    messageService
      .enviar({
        role: MessageRole.User,
        content: finalMessage,
        chat_id: currentChatId ?? undefined,
        food_data: product ?? undefined,
      })
      .then((res) => {
        const resolvedChatId = res.chat_id;

        if (!currentChatId) {
          // Título otimista alinhado ao backend (_chat_title): nome do produto
          // escaneado quando houver, senão a mensagem truncada até a 4ª palavra.
          const title = productName
            ? productName.slice(0, 255)
            : truncateTitle(finalMessage) || "Nova conversa";
          addChat({
            id: resolvedChatId,
            title,
            created_at: new Date().toISOString(),
            is_active: true,
            is_open: true,
            image_url:
              product?.product.image_front_url ||
              product?.product.image_url ||
              null,
            severity: res.verdict,
            messages: "",
          });
          // Já temos as mensagens otimistas deste chat; evita refetch (e perda da
          // imagem em blob local) ao trocar o activeId para o id real.
          fetchedChatsRef.current.add(resolvedChatId);
          setActiveId(resolvedChatId);

          setMessagesByChat((prev) => {
            const tempMessages = prev[NEW_CHAT_KEY] ?? [];
            const rest = { ...prev };
            delete rest[NEW_CHAT_KEY];
            return {
              ...rest,
              [resolvedChatId]: tempMessages.map((m) =>
                m.id === pendingMsg.id
                  ? {
                      ...m,
                      text: res.response,
                      pending: false,
                      verdict: res.verdict,
                      recommendsDoctor: res.recommends_doctor,
                    }
                  : m,
              ),
            };
          });
        } else {
          setMessagesByChat((prev) => ({
            ...prev,
            [resolvedChatId]: (prev[resolvedChatId] ?? []).map((m) =>
              m.id === pendingMsg.id
                ? {
                    ...m,
                    text: res.response,
                    pending: false,
                    verdict: res.verdict,
                    recommendsDoctor: res.recommends_doctor,
                  }
                : m,
            ),
          }));
        }
      })
      .catch(() => {
        const chatKey = currentChatId ?? NEW_CHAT_KEY;
        setMessagesByChat((prev) => ({
          ...prev,
          [chatKey]: (prev[chatKey] ?? []).map((m) =>
            m.id === pendingMsg.id
              ? {
                  ...m,
                  text: "Erro ao processar sua mensagem. Tente novamente.",
                  pending: false,
                }
              : m,
          ),
        }));
      });
  };

  return {
    messages,
    isChatPending,
    handleSend,
    clearMessages,
    loading,
    error,
  };
};
