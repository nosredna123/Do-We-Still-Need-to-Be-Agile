import { useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '../services/userService.ts'
import { useUserStore } from '@/stores/userStore.ts'
import type { CreateUserRequest, UpdateUserRequest } from '../../chat/types'

export function useCreateUser() {
  const setUser = useUserStore((state) => state.setUser)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateUserRequest) => userService.createUser(data),
    onSuccess: (user) => {
      setUser(user)
      queryClient.setQueryData(['me'], user)
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-categories'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-evolution'] })
      queryClient.invalidateQueries({ queryKey: ['recent-transactions'] })
    },
  })
}

export function useUpdateUser() {
  const { user, setUser } = useUserStore()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UpdateUserRequest) => {
      if (!user?.id) throw new Error('No user ID found')
      return userService.updateUser(user.id.toString(), data)
    },
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
      queryClient.setQueryData(['me'], updatedUser)
    },
  })
}
