import apiClient from '@/lib/api/api-client'
import type { RecurrenceInput, RecurrenceUpdate } from '@/features/chat/types'

// Define the response type locally or export it if needed elsewhere
interface RecurrentTransactionRead {
  id: number
  amount: number
  description: string
  transaction_type: 'income' | 'expense'
  frequency: string
  day: number
  active: boolean
  category_id?: number
}

export const recurrenceService = {
  async createRecurrence(
    payload: RecurrenceInput
  ): Promise<RecurrentTransactionRead> {
    const { data } = await apiClient.post<RecurrentTransactionRead>(
      '/api/v1/recurrent',
      payload
    )
    return data
  },

  async updateRecurrence(
    recurrenceId: number,
    payload: RecurrenceUpdate
  ): Promise<RecurrentTransactionRead> {
    const { data } = await apiClient.patch<RecurrentTransactionRead>(
      `/api/v1/recurrent/${recurrenceId}`,
      payload
    )
    return data
  },

  // Helper to standardizing salary creation payload
  createSalaryPayload(amount: number, payday: number): RecurrenceInput {
    return {
      amount,
      day: payday,
      description: 'Salário',
      transaction_type: 'income',
      frequency: 'monthly',
      active: true,
      category_id: null,
    }
  },
}
