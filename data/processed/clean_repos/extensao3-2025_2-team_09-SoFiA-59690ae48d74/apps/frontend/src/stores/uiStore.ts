import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ModalType = 'onboarding' | 'settings' | null

interface UIState {
  isSidebarOpen: boolean
  activeModal: ModalType
  toggleSidebar: () => void
  setSidebarOpen: (isOpen: boolean) => void
  openModal: (modal: ModalType) => void
  closeModal: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      isSidebarOpen: true,
      activeModal: null,
      toggleSidebar: () =>
        set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
      openModal: (modal) => set({ activeModal: modal }),
      closeModal: () => set({ activeModal: null }),
    }),
    {
      name: 'ui-store',
      partialize: (state) => ({
        isSidebarOpen: state.isSidebarOpen,
      }),
    }
  )
)
