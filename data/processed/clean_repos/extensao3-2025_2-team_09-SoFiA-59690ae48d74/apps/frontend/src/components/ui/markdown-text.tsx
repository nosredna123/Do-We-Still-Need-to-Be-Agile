import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface MarkdownTextProps {
  content: string
  variant?: 'default' | 'inline'
  className?: string
}

export const MarkdownText = memo(
  ({ content, variant = 'default' }: MarkdownTextProps) => {
    const isInline = variant === 'inline'

    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ ...props }) => (
            <a
              {...props}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            />
          ),
          p: ({ children }) => {
            if (isInline) return <span className="inline">{children}</span>
            return <p className="mb-4 last:mb-0 leading-7">{children}</p>
          },
        }}
      >
        {content}
      </ReactMarkdown>
    )
  }
)

MarkdownText.displayName = 'MarkdownText'
