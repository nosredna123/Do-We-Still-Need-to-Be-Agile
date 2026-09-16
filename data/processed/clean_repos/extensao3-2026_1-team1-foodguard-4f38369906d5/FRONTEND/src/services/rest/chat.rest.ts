import api from "@/config/api";
import type { Chat, PaginatedResponse } from "@/models/chat.model";

const baseUrl: string = "/chats";

const PAGE_LIMIT = 100;

export const chatRest = {
  getChats: (): Promise<PaginatedResponse<Chat>> => {
    return api.get(`${baseUrl}/`, { limit: PAGE_LIMIT });
  },

  deleteChat: (id: string): Promise<void> => {
    return api.delete(`${baseUrl}/${id}/`);
  },
};
