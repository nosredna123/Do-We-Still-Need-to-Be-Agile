import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ChatInputArea } from '@/features/chat/components/ChatInputArea'
import { ChatWelcomeScreen } from '@/features/chat/components/ChatWelcomeScreen'
import { ChatMessageList } from '@/features/chat/components/ChatMessageList'
import { useMessages, useSendMessage } from '@/features/chat/hooks/useMessages'
import { useCreateSession } from '@/features/chat/hooks/useSessions'
import { useChatStore } from '@/stores/chatStore'
import { useSessions, useUpdateSession } from '@/features/chat/hooks/useSessions'
import { Button } from '@/components/ui/button'
import { Pencil, Trash } from 'lucide-react'
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { useDeleteSession } from '@/features/chat/hooks/useSessions'
import { useNavigate } from 'react-router-dom'

const Chat = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const { setActiveSessionId, clearActiveSession } = useChatStore()

  useEffect(() => {
    if (sessionId) {
      setActiveSessionId(sessionId)
    } else {
      // se necessário alguma lógica quando não há sessionId
    }
    clearActiveSession()
  }, [sessionId, setActiveSessionId, clearActiveSession])

  const { data: messages = [] } = useMessages(sessionId || null)
  const { mutate: sendMessage, isPending: isSending } = useSendMessage()
  const { mutate: createSession, isPending: isCreating } = useCreateSession()
  const isTyping = isSending || isCreating
  const hasMessages = messages.length > 0


  const handleSend = (text: string) => {
    if (!text.trim()) return
    if (sessionId) {
      sendMessage({
        sessionId,
        data: { message: text, model_preference: 'remote' },
      })
    } else {
      createSession({
        message: text,
        model_preference: 'remote',
      })
    }
  }

  const { data: sessions = [] } = useSessions()
  const { mutate: updateSession, isPending: isUpdating } = useUpdateSession()

  const currentSession = sessions.find((s) => s.id === Number(sessionId))

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newTitle, setNewTitle] = useState('')

  useEffect(() => {
    if (isDialogOpen) {
      setNewTitle(currentSession?.title ?? '')
    }
  }, [isDialogOpen, currentSession])

  const handleSaveTitle = () => {
    if (!sessionId) return
    const trimmed = newTitle.trim()
    if (!trimmed) return

    updateSession(
      {
        sessionId,
        data: { title: trimmed },
      },
      {
        onSuccess: () => {
          setIsDialogOpen(false)
          setNewTitle('')
        },
      }
    )
  }

  const { mutate: deleteSession, isPending: isDeleting } = useDeleteSession()
  const navigate = useNavigate()
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const handleDeleteSession = () => {
    if (!sessionId) return

    deleteSession(sessionId, {
      onSuccess: () => {
        setIsDeleteDialogOpen(false)
        navigate('/')
      },
    })
  }

  return (
    <div className="flex flex-col h-full bg-background">
      <header className="px-8 py-6 border-b border-border flex flex-item items-center justify-between">
        <h1 className="text-xl font-semibold text-foreground text-center">
          {currentSession?.title || 'Nova Conversa'}
        </h1>

        {hasMessages && (
          <div className="gap-4 flex">
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-[] text-[] hover:bg-[#bdbdbd]/50 hover:text-[]">
                  <Pencil />
                  Editar Título
                </Button>
              </DialogTrigger>

              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-center">Editar Título do Chat</DialogTitle>
                </DialogHeader>

                <div className="flex gap-4 items-center">
                  <Input
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder={currentSession?.title ?? 'Novo título'}
                  />

                  <Button
                    className="bg-[#4e6e97] text-white hover:bg-[#3b5a7a]"
                    onClick={handleSaveTitle}
                    disabled={
                      isUpdating ||
                      newTitle.trim().length === 0 ||
                      newTitle.trim() === (currentSession?.title ?? '').trim()
                    }
                  >
                    {isUpdating ? 'Salvando...' : 'Salvar'}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-[] text-[] hover:bg-[#fa0202]/50 hover:text-[]">
                  <Trash />
                  Excluir Chat
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-center">Excluir Chat</DialogTitle>
                </DialogHeader>
                <p className="mb-4">Tem certeza que deseja excluir este chat? Esta ação não pode ser desfeita.</p>
                <div className="flex justify-end gap-4">
                  <Button
                    variant="outline"
                    onClick={() => setIsDeleteDialogOpen(false)}
                  >
                    Cancelar
                  </Button>
                  <Button
                    className="bg-[#fa0202] text-white hover:bg-[#c70101]"
                    onClick={handleDeleteSession}
                  >
                    {isDeleting ? 'Excluindo...' : 'Excluir'}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        )}
      </header>

      <div className="flex-1 overflow-hidden flex flex-col relative">
        {!sessionId ? (
          <ChatWelcomeScreen onSuggestionClick={handleSend} />
        ) : (
          <ChatMessageList messages={messages} isTyping={isTyping} />
        )}
      </div>

      <ChatInputArea onSend={handleSend} />
    </div>
  )
}

export default Chat
