import { chatRest } from "./rest/chat.rest"
import type { Chat } from "@/models/chat.model"

export const chatService = {

    listar: async (): Promise<Chat[]> => {
        const response = await chatRest.getChats()
        return response.results
    },

    deletar: async (chatId: string): Promise<void> => {
        return chatRest.deleteChat(chatId)
    }
}
