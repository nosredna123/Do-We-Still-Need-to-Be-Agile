import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { MonthlyEvolution } from '../types'
import { Skeleton } from '@/components/ui/skeleton'

interface Props {
  data?: MonthlyEvolution[]
  isLoading: boolean
}

const chartConfig = {
  total_income: {
    label: 'Receitas',
    color: '#07ad18',
  },
  total_expense: {
    label: 'Despesas',
    color: '#d92b14',
  },
}

export function EvolutionBarChart({ data, isLoading }: Props) {
  if (isLoading) {
    return <Skeleton className="h-[400px] w-full rounded-xl" />
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução Mensal (Últimos 6 meses)</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data || []}>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="hsl(var(--border))"
              />
              <XAxis
                dataKey="month"
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `R$${value}`}
              />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent indicator="dashed" />}
              />
              <Legend />
              <Bar
                dataKey="total_income"
                fill="var(--color-total_income)"
                radius={4}
                name="Receitas"
              />
              <Bar
                dataKey="total_expense"
                fill="var(--color-total_expense)"
                radius={4}
                name="Despesas"
              />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
