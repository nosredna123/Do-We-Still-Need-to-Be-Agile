import apiClient from '@/lib/api/api-client'
import type {
  DashboardSummary,
  CategorySpending,
  MonthlyEvolution,
  Transaction,
} from '../types'

export const analyticsService = {
  async getSummary(month?: number, year?: number): Promise<DashboardSummary> {
    const params = new URLSearchParams()
    if (month) params.append('month', month.toString())
    if (year) params.append('year', year.toString())

    const { data } = await apiClient.get<DashboardSummary>(
      `/api/v1/analytics/summary?${params.toString()}`
    )
    return data
  },

  async getCategorySpending(
    month?: number,
    year?: number
  ): Promise<CategorySpending[]> {
    const params = new URLSearchParams()
    if (month) params.append('month', month.toString())
    if (year) params.append('year', year.toString())

    const { data } = await apiClient.get<CategorySpending[]>(
      `/api/v1/analytics/spending-by-category?${params.toString()}`
    )
    return data
  },

  async getMonthlyEvolution(months: number = 6): Promise<MonthlyEvolution[]> {
    const { data } = await apiClient.get<MonthlyEvolution[]>(
      `/api/v1/analytics/monthly-evolution?months=${months}`
    )
    return data
  },

  async getRecentTransactions(limit: number = 5): Promise<Transaction[]> {
    const { data } = await apiClient.get<Transaction[]>(
      `/api/v1/transactions?limit=${limit}`
    )
    return data
  },

  async getAllTransactions(): Promise<Transaction[]> {
    const { data } = await apiClient.get<Transaction[]>(
      `/api/v1/transactions`
    )
    return data
  }
}
