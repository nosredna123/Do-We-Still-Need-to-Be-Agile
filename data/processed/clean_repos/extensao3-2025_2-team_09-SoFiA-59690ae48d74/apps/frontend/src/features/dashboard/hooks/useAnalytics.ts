import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { analyticsService } from '../services/analyticsService'
import { formatters } from '@/lib/formatters'

const dashboardQueryOptions = {
  staleTime: 0,
  refetchOnMount: true,
  refetchOnWindowFocus: true,
}

export function useDashboardSummary(month: number, year: number) {
  return useQuery({
    queryKey: ['dashboard-summary', month, year],
    queryFn: () => analyticsService.getSummary(month, year),
    placeholderData: keepPreviousData,
    ...dashboardQueryOptions, // Apply realtime rules
    select: (data) => ({
      ...data,
      total_balance: formatters.fromCents(data.total_balance),
      total_income: formatters.fromCents(data.total_income),
      total_expense: formatters.fromCents(data.total_expense),
      total_savings: formatters.fromCents(data.total_savings),
    }),
  })
}

export function useCategorySpending(month: number, year: number) {
  return useQuery({
    queryKey: ['dashboard-categories', month, year],
    queryFn: () => analyticsService.getCategorySpending(month, year),
    placeholderData: keepPreviousData,
    ...dashboardQueryOptions,
    select: (data) =>
      data.map((item) => ({
        ...item,
        amount: formatters.fromCents(item.amount),
      })),
  })
}

export function useMonthlyEvolution(months: number = 6) {
  return useQuery({
    queryKey: ['dashboard-evolution', months],
    queryFn: () => analyticsService.getMonthlyEvolution(months),
    // Removed the 10 minute staleTime override
    ...dashboardQueryOptions,
    select: (data) =>
      data.map((item) => ({
        ...item,
        total_income: formatters.fromCents(item.total_income),
        total_expense: formatters.fromCents(item.total_expense),
        balance: formatters.fromCents(item.balance),
      })),
  })
}

export function useRecentTransactions(limit: number = 5) {
  return useQuery({
    queryKey: ['recent-transactions', limit],
    queryFn: () => analyticsService.getRecentTransactions(limit),
    ...dashboardQueryOptions,
    select: (data) =>
      data.map((tx) => ({
        ...tx,
        amount: formatters.fromCents(tx.amount),
      })),
  })
}

export function useAllTransactions() {
  return useQuery({
    queryKey: ['all-transactions'],
    queryFn: () => analyticsService.getAllTransactions(),
    ...dashboardQueryOptions,
    select: (data) =>
      data.map((tx) => ({
        ...tx,
        amount: formatters.fromCents(tx.amount),
      })),
  })
}