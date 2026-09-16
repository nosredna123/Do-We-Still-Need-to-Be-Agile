import { useRef, useEffect, useMemo } from 'react'
import MessageBubble from '@/components/MessageBubble'
import TypingIndicator from '@/components/TypingIndicator'
import type { Message } from '@/features/chat/types'

interface ChatMessageListProps {
  messages: Message[]
  isTyping?: boolean
}

export function ChatMessageList({ messages, isTyping }: ChatMessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const lastMessageRef = useRef<HTMLDivElement | null>(null)


  const displayMessages = useMemo(() => {
    const msgs = messages ? [...messages] : []

    // Se não existir createdAt, tentamos ordenar por id numérico
    const safeGetTime = (m: any) => {
      if (m.createdAt) {
        const t = new Date(m.createdAt).getTime()
        return Number.isFinite(t) ? t : 0
      }
      // fallback: se id for número
      if (typeof m.id === 'number') return m.id
      // fallback final
      return 0
    }

    return msgs.sort((a, b) => safeGetTime(a) - safeGetTime(b))
  }, [messages])

  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
      })
    } else if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [displayMessages.length, isTyping])
  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6">
      <div className="max-w-3xl mx-auto space-y-4">
        {displayMessages.map((msg, index) => {
          const isLast = index === displayMessages.length - 1
          return (
            <div
              key={msg.id ?? `msg-${index}`}
              ref={isLast ? lastMessageRef : undefined}
            >
              <MessageBubble role={msg.role} content={msg.content} />
            </div>
          )
        })}
        {isTyping && <TypingIndicator />}
      </div>
    </div>
  )
}
