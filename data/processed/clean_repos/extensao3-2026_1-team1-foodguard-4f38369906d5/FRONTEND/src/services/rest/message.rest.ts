import api from "@/config/api";
import type {
  Message,
  MessageCreateRequest,
  MessageCreateResponse,
} from "@/models/message.model";
import type { PaginatedResponse } from "@/models/chat.model";

const baseUrl: string = "/chats";

const PAGE_LIMIT = 100;

export const messageRest = {
  getMessages: (chatId: string): Promise<PaginatedResponse<Message>> => {
    return api.get(`${baseUrl}/${chatId}/messages/`, { limit: PAGE_LIMIT });
  },

  sendMessage: (body: MessageCreateRequest): Promise<MessageCreateResponse> => {
    return api.post(`${baseUrl}/message/send/`, body);
  },
};
