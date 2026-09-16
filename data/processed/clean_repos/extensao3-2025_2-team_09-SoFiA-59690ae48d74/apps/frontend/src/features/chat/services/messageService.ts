import type {
  Message,
  SendMessageRequest,
  SendMessageResponse,
  PaginatedResponse,
} from '../types'
import apiClient from '@/lib/api/api-client'

export const messageService = {
  async getMessages(sessionId: string): Promise<Message[]> {
    const { data } = await apiClient.get<PaginatedResponse<Message>>(
      `/api/v1/chat/sessions/${sessionId}/messages`
    )
    return data.items || []
  },

  async sendMessage(
    sessionId: string,
    data: SendMessageRequest
  ): Promise<SendMessageResponse> {
    const { data: responseData } = await apiClient.post<SendMessageResponse>(
      `/api/v1/chat/sessions/${sessionId}/messages`,
      data
    )
    return responseData
  },
}
