import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sessionService } from '../services/sessionService'
import { useUserStore } from '@/stores/userStore'
import { useChatStore } from '@/stores/chatStore'
import { useNavigate } from 'react-router-dom'
import type {
  ChatSession,
  UpdateSessionRequest,
  CreateSessionRequest,
  Message,
  CreateSessionResponse,
} from '../types'

export function useSessions() {
  const user = useUserStore((state) => state.user)

  return useQuery({
    queryKey: ['sessions', user?.id],
    queryFn: () => {
      if (!user?.id) return []
      return sessionService.getSessions(user.id.toString())
    },
    enabled: !!user?.id,
  })
}

export function useCreateSession() {
  const queryClient = useQueryClient()
  const user = useUserStore((state) => state.user)
  const navigate = useNavigate()
  const setActiveSessionId = useChatStore((state) => state.setActiveSessionId)

  return useMutation({
    mutationFn: async (data: Omit<CreateSessionRequest, 'user_id'>) => {
      const currentUser = user || useUserStore.getState().user
      if (!currentUser?.id) throw new Error('User not found')
      return sessionService.createSession({ ...data })
    },
    onSuccess: (response: CreateSessionResponse, variables) => {
      const userId = user?.id || useUserStore.getState().user?.id
      queryClient.invalidateQueries({ queryKey: ['sessions', userId] })
      const newSessionId = response.session_id
      const sessionIdStr = newSessionId.toString()
      
      // Save session to store for persistence
      setActiveSessionId(sessionIdStr)
      
      const initialMessages: Message[] = [
        {
          id: -1,
          role: 'user',
          content: variables.message,
          created_at: new Date().toISOString(),
          meta_data: null,
        },
        {
          id: -2,
          role: 'assistant',
          content: response.response,
          created_at: new Date().toISOString(),
          meta_data: null,
        },
      ]
      queryClient.setQueryData(['messages', sessionIdStr], initialMessages)
      queryClient.invalidateQueries({ queryKey: ['messages', sessionIdStr] })
      navigate(`/chat/${sessionIdStr}`)
    },
  })
}

export function useDeleteSession() {
  const queryClient = useQueryClient()
  const user = useUserStore((state) => state.user)
  const { activeSessionId, clearActiveSession } = useChatStore()

  return useMutation({
    mutationFn: (sessionId: string) => sessionService.deleteSession(sessionId),
    onMutate: async (sessionId) => {
      await queryClient.cancelQueries({ queryKey: ['sessions', user?.id] })

      const previousSessions = queryClient.getQueryData<ChatSession[]>([
        'sessions',
        user?.id,
      ])

      queryClient.setQueryData<ChatSession[]>(['sessions', user?.id], (old) =>
        old ? old.filter((session) => session.id.toString() !== sessionId) : []
      )
      
      // Clear active session if it's the one being deleted
      if (activeSessionId === sessionId) {
        clearActiveSession()
      }

      return { previousSessions }
    },
    onError: (_err, _newTodo, context) => {
      queryClient.setQueryData(
        ['sessions', user?.id],
        context?.previousSessions
      )
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions', user?.id] })
    },
  })
}

export function useUpdateSession() {
  const queryClient = useQueryClient()
  const user = useUserStore((state) => state.user)

  return useMutation({
    mutationFn: ({
      sessionId,
      data,
    }: {
      sessionId: string
      data: UpdateSessionRequest
    }) => sessionService.updateSession(sessionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions', user?.id] })
    },
  })
}
