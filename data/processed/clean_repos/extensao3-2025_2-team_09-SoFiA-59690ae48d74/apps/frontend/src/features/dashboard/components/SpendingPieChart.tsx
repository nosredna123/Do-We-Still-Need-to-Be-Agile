import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import type { CategorySpending } from '../types'
import { Skeleton } from '@/components/ui/skeleton'

interface Props {
  data?: CategorySpending[]
  isLoading: boolean
}

const COLORS = [
  '#07ad18',
  '#14d9c5',
  '#9534eb',
  '#6823e8',
  '#d92b14',
  '#acacad',
]

export function SpendingPieChart({ data, isLoading }: Props) {
  if (isLoading) {
    return <Skeleton className="h-[400px] w-full rounded-xl" />
  }

  const hasData = data && data.length > 0
  const chartConfig = hasData
    ? data.reduce((acc, item, index) => {
        acc[item.category_name] = {
          label: item.category_name,
          color: COLORS[index % COLORS.length],
        }
        return acc
      }, {} as never)
    : {}

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <CardTitle>Gastos por Categoria</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        {!hasData ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            Sem dados para este período
          </div>
        ) : (
          <>
            <ChartContainer
              config={chartConfig}
              className="mx-auto aspect-square max-h-[300px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="amount"
                    nameKey="category_name"
                  >
                    {data.map((_entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
            <div className="grid grid-cols-2 gap-3 mt-6 pb-6">
              {data.map((category, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span
                    className="text-sm text-foreground truncate max-w-[100px]"
                    title={category.category_name}
                  >
                    {category.category_name}
                  </span>
                  <span className="text-sm font-semibold text-foreground ml-auto">
                    {category.percentage}%
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
