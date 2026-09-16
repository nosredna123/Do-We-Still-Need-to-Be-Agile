import MetricCard from '@/components/MetricCard'
import type { DashboardSummary } from '../types'
import { Skeleton } from '@/components/ui/skeleton'

interface Props {
  data?: DashboardSummary
  isLoading: boolean
}

export function DashboardSummaryCards({ data, isLoading }: Props) {
  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32 w-full rounded-xl" />
        ))}
      </div>
    )
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(val)

  const formatPct = (val: number) => {
    const sign = val >= 0 ? '+' : ''
    return `${sign}${val.toFixed(1)}%`
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Saldo Total"
        value={formatCurrency(data.total_balance)}
        change="Saldo Vitalício"
        trend="neutral"
        icon="wallet"
      />
      <MetricCard
        title="Receitas"
        value={formatCurrency(data.total_income)}
        change={`${formatPct(data.income_change_pct)} vs mês anterior`}
        trend={data.income_change_pct >= 0 ? 'up' : 'down'}
        icon="income"
      />
      <MetricCard
        title="Despesas"
        value={formatCurrency(data.total_expense)}
        change={`${formatPct(data.expense_change_pct)} vs mês anterior`}
        trend={data.expense_change_pct <= 0 ? 'up' : 'down'}
        icon="expense"
      />
      <MetricCard
        title="Economia"
        value={formatCurrency(data.total_savings)}
        change={`${formatPct(data.savings_change_pct)} vs mês anterior`}
        trend={data.savings_change_pct >= 0 ? 'up' : 'down'}
        icon="savings"
      />
    </div>
  )
}
