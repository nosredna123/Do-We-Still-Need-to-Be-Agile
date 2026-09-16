import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
} from '../../chat/types'
import apiClient from '@/lib/api/api-client.ts'

export const userService = {
  async createUser(payload: CreateUserRequest): Promise<User> {
    const { data } = await apiClient.post<User>('/api/v1/users', payload)
    return data
  },

  async updateUser(userId: string, payload: UpdateUserRequest): Promise<User> {
    const { data } = await apiClient.put<User>(
      `/api/v1/users/${userId}`,
      payload
    )
    return data
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await apiClient.get<User>('/api/v1/users/me')
    return data
  },
}
