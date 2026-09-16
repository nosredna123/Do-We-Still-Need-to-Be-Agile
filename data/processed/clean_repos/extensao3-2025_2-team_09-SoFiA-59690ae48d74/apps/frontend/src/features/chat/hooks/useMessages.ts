import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { messageService } from '../services/messageService'
import type { Message, SendMessageRequest } from '../types'

export function useMessages(sessionId: string | null) {
  return useQuery({
    queryKey: ['messages', sessionId],
    queryFn: () => {
      if (!sessionId) return []
      return messageService.getMessages(sessionId)
    },
    enabled: !!sessionId,
    // CHANGED: Only use placeholder data if we are switching between valid sessions.
    // If sessionId is null (New Chat), we want to clear immediately, not show old messages.
    placeholderData: (previousData, previousQuery) => {
      if (!sessionId) return undefined
      return previousData
    },
    select: (data) => {
      if (!data) return []
      // CHANGED: Strict chronological order (Oldest -> Newest)
      // This ensures new messages (Date.now()) always appear at the bottom
      return [...data].sort((a, b) => {
        const dateA = new Date(a.created_at).getTime()
        const dateB = new Date(b.created_at).getTime()
        return dateA - dateB
      })
    },
  })
}

export function useSendMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      sessionId,
      data,
    }: {
      sessionId: string
      data: SendMessageRequest
    }) => messageService.sendMessage(sessionId, data),

    onMutate: async ({ sessionId, data }) => {
      await queryClient.cancelQueries({ queryKey: ['messages', sessionId] })
      const previousMessages = queryClient.getQueryData<Message[]>([
        'messages',
        sessionId,
      ])

      const userMessage: Message = {
        id: Date.now(),
        role: 'user',
        content: data.message,
        created_at: new Date().toISOString(),
        meta_data: null,
      }
      queryClient.setQueryData<Message[]>(['messages', sessionId], (old) => {
        return old ? [...old, userMessage] : [userMessage]
      })
      return { previousMessages }
    },

    onError: (_err, { sessionId }, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData(
          ['messages', sessionId],
          context.previousMessages
        )
      }
    },

    onSuccess: (data, { sessionId }) => {
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        created_at: new Date().toISOString(),
        meta_data: null,
      }
      queryClient.setQueryData<Message[]>(['messages', sessionId], (old) => {
        return old ? [...old, assistantMessage] : [assistantMessage]
      })
    },
  })
}
