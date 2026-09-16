import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useUserStore } from '@/stores/userStore'
import { useUIStore } from '@/stores/uiStore'
import { userService } from '@/features/auth/services/userService.ts'

export function useAuthCheck() {
  const setUser = useUserStore((state) => state.setUser)
  const clearUser = useUserStore((state) => state.clearUser)
  const openModal = useUIStore((state) => state.openModal)
  const activeModal = useUIStore((state) => state.activeModal)

  const { data, isError, error, isSuccess } = useQuery({
    queryKey: ['me'],
    queryFn: userService.getCurrentUser,
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: false,
  })

  useEffect(() => {
    if (isSuccess && data) {
      setUser(data)
      if (activeModal === 'onboarding') {
        useUIStore.getState().closeModal()
      }
    }
    if (isError) {
      // @ts-expect-error axios error typing
      const status = error?.response?.status
      if (status === 404 || status === 401) {
        clearUser()
        if (activeModal !== 'onboarding') {
          openModal('onboarding')
        }
      }
    }
  }, [
    isSuccess,
    data,
    isError,
    error,
    setUser,
    clearUser,
    openModal,
    activeModal,
  ])

  return { isLoading: !isSuccess && !isError }
}
