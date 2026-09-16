import type { Transaction } from '@/features/chat/types'

export interface DashboardSummary {
  total_balance: number
  total_income: number
  total_expense: number
  total_savings: number
  income_change_pct: number
  expense_change_pct: number
  savings_change_pct: number
}

export interface CategorySpending {
  category_name: string
  amount: number
  percentage: number
}

export interface MonthlyEvolution {
  month: string
  total_income: number
  total_expense: number
  balance: number
}

export interface DashboardFilters {
  month: number
  year: number
}

// Re-export Transaction for convenience in Dashboard
export type { Transaction }
