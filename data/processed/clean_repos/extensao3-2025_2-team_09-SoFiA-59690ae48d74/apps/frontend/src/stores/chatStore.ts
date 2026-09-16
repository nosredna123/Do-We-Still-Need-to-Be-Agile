import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ChatState {
  activeSessionId: string | null
  setActiveSessionId: (sessionId: string | null) => void
  clearActiveSession: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      activeSessionId: null,
      setActiveSessionId: (sessionId) => set({ activeSessionId: sessionId }),
      clearActiveSession: () => set({ activeSessionId: null }),
    }),
    {
      name: 'chat-store',
    }
  )
)
