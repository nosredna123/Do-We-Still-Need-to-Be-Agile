import SuggestionCard from '@/components/SuggestionCard'

interface ChatWelcomeScreenProps {
  onSuggestionClick: (text: string) => void
}

export function ChatWelcomeScreen({
  onSuggestionClick,
}: ChatWelcomeScreenProps) {
  const suggestions = [
    'Fiz compras hoje no supermercado',
    'Jantei fora ontem',
    'Voltei de Uber para casa ontem',
    'Quanto já gastei com alimentação este mês?',
    'Como posso economizar mais?',
    'Quais são minhas maiores despesas?',
  ]

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-8 pb-32 animate-in fade-in duration-500">
      <div className="w-full max-w-3xl space-y-8">
        <h2 className="text-4xl font-bold text-center text-foreground">
          Como posso lhe ajudar?
        </h2>
        <div>
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Sugestões rápidas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestions.map((suggestion, index) => (
              <SuggestionCard
                key={index}
                text={suggestion}
                onClick={() => onSuggestionClick(suggestion)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
