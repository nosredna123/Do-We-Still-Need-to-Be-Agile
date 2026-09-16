import { useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button.tsx'
import { Input } from '@/components/ui/input.tsx'

interface ChatInputAreaProps {
  onSend: (message: string) => void
  disabled?: boolean
  isLoading?: boolean
  placeholder?: string
}

export function ChatInputArea({
  onSend,
  disabled,
  isLoading,
  placeholder = 'Digite uma mensagem...',
}: ChatInputAreaProps) {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (!message.trim() || isLoading || disabled) return
    onSend(message.trim())
    setMessage('')
  }

  return (
    <div className="px-8 pb-8 bg-background">
      <div className="max-w-3xl mx-auto space-y-2">
        <div className="relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder={placeholder}
            className="pr-12 dark:bg-[#1E1E1E] py-6 rounded-full focus-visible:ring-3 px-6"
            disabled={disabled || isLoading}
            autoFocus
          />
          <Button
            onClick={handleSend}
            size="icon"
            disabled={disabled || isLoading || !message.trim()}
            className="bg-[#4e6e97] absolute right-2 top-1/2 -translate-y-1/2 rounded-full h-9 w-9 cursor-pointer dark:bg-[#3b5a7a] dark:text-white hover:bg-[#3b5a7a] hover:text-white dark:hover:text-white"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <div className="text-center text-sm text-[#4e6e97] py-1 dark:text-[#ffffff]/80">
          Usando o Gemini 2.5 Flash Lite
        </div>
      </div>
    </div>
  )
}
