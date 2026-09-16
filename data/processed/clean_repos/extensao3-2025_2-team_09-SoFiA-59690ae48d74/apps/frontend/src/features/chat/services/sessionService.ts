import type {
  ChatSession,
  UpdateSessionRequest,
  CreateSessionRequest,
  CreateSessionResponse,
} from '../types'
import apiClient from '@/lib/api/api-client'

export const sessionService = {
  async getSessions(userId: string): Promise<ChatSession[]> {
    const { data } = await apiClient.get<ChatSession[]>(
      `/api/v1/chat/sessions?user_id=${userId}`
    )
    return data
  },

  async createSession(
    payload: CreateSessionRequest
  ): Promise<CreateSessionResponse> {
    const { data } = await apiClient.post<CreateSessionResponse>(
      '/api/v1/chat/sessions',
      payload
    )
    return data
  },

  async deleteSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/api/v1/chat/sessions/${sessionId}`)
  },

  async updateSession(
    sessionId: string,
    payload: UpdateSessionRequest
  ): Promise<ChatSession> {
    const { data } = await apiClient.put<ChatSession>(
      `/api/v1/chat/sessions/${sessionId}`,
      payload
    )
    return data
  },
}
