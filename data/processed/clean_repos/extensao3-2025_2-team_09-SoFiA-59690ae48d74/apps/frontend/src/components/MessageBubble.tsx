import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism' // VSCode-like dark theme
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { User, Bot } from 'lucide-react'

interface MessageBubbleProps {
  role: 'user' | 'assistant'
  content: string
}

const MessageBubble = memo(({ role, content }: MessageBubbleProps) => {
  const isUser = role === 'user'

  return (
    <div
      className={cn(
        'flex w-full gap-3 py-4 animate-in fade-in slide-in-from-bottom-2',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <Avatar className="h-8 w-8 border">
        {isUser ? (
          <>
            <AvatarImage src="" />
            <AvatarFallback className="bg-[#4e6e97] text-[#dbeafe]">
              <User className="h-4 w-4" />
            </AvatarFallback>
          </>
        ) : (
          <AvatarFallback className="bg-muted text-foreground">
            <Bot className="h-4 w-4" />
          </AvatarFallback>
        )}
      </Avatar>

      {/* Message Content */}
      <div
        className={cn(
          'relative max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm',
          isUser
            ? 'bg-[#4e6e97] text-[#dbeafe] rounded-tr-none'
            : 'bg-muted text-foreground rounded-tl-none border border-border'
        )}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // Paragraphs: Add margin only if it's not the last element
            p: ({ children }) => (
              <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
            ),

            // Links: Style based on background color
            a: ({ href, children }) => (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  'font-medium underline underline-offset-4',
                  isUser
                    ? 'text-primary-foreground hover:text-primary-foreground/80'
                    : 'text-primary hover:text-primary/80'
                )}
              >
                {children}
              </a>
            ),

            // Lists
            ul: ({ children }) => (
              <ul className="mb-2 list-disc pl-4 space-y-1">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="mb-2 list-decimal pl-4 space-y-1">{children}</ol>
            ),
            li: ({ children }) => <li>{children}</li>,

            // Headings
            h1: ({ children }) => (
              <h1 className="text-lg font-bold mb-2 mt-4">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-base font-semibold mb-2 mt-3">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-sm font-semibold mb-1 mt-2">{children}</h3>
            ),

            // Blockquotes
            blockquote: ({ children }) => (
              <blockquote className="border-l-2 border-primary/50 pl-4 italic my-2">
                {children}
              </blockquote>
            ),

            // Code handling (Inline vs Block)
            code: ({ className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '')
              const isInline = !match

              if (isInline) {
                return (
                  <code
                    className={cn(
                      'rounded px-1 py-0.5 font-mono text-xs font-semibold',
                      isUser
                        ? 'bg-primary-foreground/20 text-primary-foreground'
                        : 'bg-muted-foreground/20 text-foreground'
                    )}
                    {...props}
                  >
                    {children}
                  </code>
                )
              }

              return (
                <div className="rounded-md overflow-hidden my-3 w-full">
                  <SyntaxHighlighter
                    // @ts-expect-error type definition mismatch in lib
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{
                      margin: 0,
                      borderRadius: '0.5rem',
                      fontSize: '0.8rem',
                    }}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                </div>
              )
            },

            // Tables
            table: ({ children }) => (
              <div className="my-4 w-full overflow-y-auto rounded-lg border">
                <table className="w-full text-left">{children}</table>
              </div>
            ),
            thead: ({ children }) => (
              <thead className="bg-muted-foreground/10 uppercase text-xs font-semibold">
                {children}
              </thead>
            ),
            tbody: ({ children }) => (
              <tbody className="divide-y divide-border">{children}</tbody>
            ),
            tr: ({ children }) => (
              <tr className="hover:bg-muted-foreground/5">{children}</tr>
            ),
            th: ({ children }) => <th className="px-4 py-2">{children}</th>,
            td: ({ children }) => <td className="px-4 py-2">{children}</td>,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  )
})

MessageBubble.displayName = 'MessageBubble'

export default MessageBubble
