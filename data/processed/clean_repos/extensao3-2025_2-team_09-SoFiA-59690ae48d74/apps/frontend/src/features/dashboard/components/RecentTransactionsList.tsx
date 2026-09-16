import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import TransactionItem from '@/components/TransactionItem'
import type { Transaction } from '../types'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'

interface Props {
  data?: Transaction[]
  isLoading: boolean
}

export function RecentTransactionsList({ data, isLoading }: Props) {
  if (isLoading) {
    return <Skeleton className="h-[300px] w-full rounded-xl" />
  }

  const getIcon = (categoryName: number, type: string) => {
    if (type === 'income') return 'income'

    if (categoryName == 1) return 'entertainment'
    if (categoryName == 2) return 'transport'
    if (categoryName == 3) return 'taxes'
    if (categoryName == 4) return 'technology'
    if (categoryName == 5) return 'travel'
    if (categoryName == 6) return 'pets'
    if (categoryName == 7) return 'shopping'
    if (categoryName == 8) return 'housing'
    if (categoryName == 9) return 'education'
    if (categoryName == 10) return 'health'
    if (categoryName == 11) return 'personal'
    return 'personal'
  }

  const recentTransactions = data?.slice(0, 5) ?? []
  const allTransactions = data ?? []

  const renderTransactionItem = (t: Transaction) => {
    // Parse date correctly to avoid timezone issues
    const dateStr = String(t.reference_date)
    const [year, month, day] = dateStr.split('-').map(Number)
    const date = new Date(year, month - 1, day)
    
    return (
      <TransactionItem
        key={t.id}
        icon={
          getIcon(
            t.category_id,
            t.transaction_type
          ) as any
        }
        title={t.description}
        category={
          t.transaction_type === 'income' ? 'Receita' : 'Despesa'
        }
        amount={t.amount}
        date={date.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: 'short',
        })}
        type={t.transaction_type}
      />
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className='flex justify-between w-full'>
          Registro
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="text-primary hover:text-primary/80">
                Ver todas
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[85vh]">
              <DialogHeader>
                <DialogTitle className="text-2xl">Todas as Transações</DialogTitle>
              </DialogHeader>
              <ScrollArea className="h-[65vh] pr-4">
                <div className="space-y-0">
                  {allTransactions.length === 0 ? (
                    <p className="text-muted-foreground text-sm py-4">
                      Nenhuma transação encontrada.
                    </p>
                  ) : (
                    allTransactions.map(renderTransactionItem)
                  )}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-0">
          {recentTransactions.length === 0 ? (
            <p className="text-muted-foreground text-sm py-4">
              Nenhuma transação encontrada.
            </p>
          ) : (
            recentTransactions.map(renderTransactionItem)
          )}
        </div>
      </CardContent>
    </Card>
  )
}
