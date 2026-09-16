import { MarkdownText } from '@/components/ui/markdown-text'

interface SessionTitleProps {
  title: string
  isActive?: boolean
}

export const SessionTitle = ({ title, isActive }: SessionTitleProps) => {
  return (
    <div
      className={`truncate text-sm ${isActive ? 'font-medium' : 'font-normal'}`}
    >
      <MarkdownText
        content={title}
        variant="inline"
        className="pointer-events-none"
      />
    </div>
  )
}
