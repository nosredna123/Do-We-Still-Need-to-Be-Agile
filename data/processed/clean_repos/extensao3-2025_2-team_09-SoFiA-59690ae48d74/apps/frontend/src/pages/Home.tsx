import { useState } from 'react'
import { useUserStore } from '@/stores/userStore'
import {
  useDashboardSummary,
  useCategorySpending,
  useMonthlyEvolution,
  useRecentTransactions,
  useAllTransactions,
} from '@/features/dashboard/hooks/useAnalytics'

import { DashboardSummaryCards } from '@/features/dashboard/components/DashboardSummaryCards'
import { SpendingPieChart } from '@/features/dashboard/components/SpendingPieChart'
import { EvolutionBarChart } from '@/features/dashboard/components/EvolutionBarChart'
import { RecentTransactionsList } from '@/features/dashboard/components/RecentTransactionsList'
import { DashboardDateFilter } from '@/features/dashboard/components/DashboardDateFilter'

const Home = () => {
  const user = useUserStore((state) => state.user)

  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())
  const summaryQuery = useDashboardSummary(month, year)
  const categoryQuery = useCategorySpending(month, year)
  const evolutionQuery = useMonthlyEvolution(6)
  const allTxQuery = useAllTransactions()

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Seja bem-vindo</h1>
          <p className="text-muted-foreground mt-1">
            É bom te ver, {user?.name || 'Visitante'}!
          </p>
        </div>

        <DashboardDateFilter
          month={month}
          year={year}
          onMonthChange={setMonth}
          onYearChange={setYear}
        />
      </div>

      <DashboardSummaryCards
        data={summaryQuery.data}
        isLoading={summaryQuery.isLoading}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SpendingPieChart
          data={categoryQuery.data}
          isLoading={categoryQuery.isLoading}
        />
        <EvolutionBarChart
          data={evolutionQuery.data}
          isLoading={evolutionQuery.isLoading}
        />
      </div>

      <RecentTransactionsList
        data={allTxQuery.data}
        isLoading={allTxQuery.isLoading}
      />
    </div>
  )
}

export default Home
