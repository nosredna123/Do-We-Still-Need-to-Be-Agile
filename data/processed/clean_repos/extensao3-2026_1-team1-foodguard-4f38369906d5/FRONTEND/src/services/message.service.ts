import { messageRest } from "./rest/message.rest"
import type { Message, MessageCreateRequest, MessageCreateResponse } from "@/models/message.model"

export const messageService = {

    listar: async (chatId: string): Promise<Message[]> => {
        const response = await messageRest.getMessages(chatId)
        return response.results
    },

    enviar: async (data: MessageCreateRequest): Promise<MessageCreateResponse> => {
        return messageRest.sendMessage(data)
    }
}
