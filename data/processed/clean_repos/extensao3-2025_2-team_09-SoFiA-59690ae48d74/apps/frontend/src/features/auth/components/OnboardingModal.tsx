import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useUIStore } from '@/stores/uiStore'
import { useCreateUser } from '@/features/auth/hooks/useUser.ts'
import { Key, User, DollarSign, Calendar, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'

const formSchema = z.object({
  name: z.string().min(2, 'O nome deve ter pelo menos 2 caracteres'),
  api_key: z.string().optional(),
  salary: z.string(),
  payday: z.string().optional().refine((val) => !val || (Number(val) >= 1 && Number(val) <= 31), {
    message: 'O dia de recebimento deve estar entre 1 e 31',
  }),
})

type FormData = z.infer<typeof formSchema>

export function OnboardingModal() {
  const { activeModal } = useUIStore()
  const { mutate: createUser, isPending } = useCreateUser()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      api_key: '',
      salary: '',
      payday: '',
    },
  })

  const onSubmit = (data: FormData) => {
    const salaryValue = data.salary && data.salary.trim() !== '' ? parseInt(data.salary)*100 : undefined
    const paydayValue = data.payday && data.payday.trim() !== '' ? parseInt(data.payday) : undefined
    
    createUser({
      name: data.name,
      api_key: data.api_key || undefined,
      salary: salaryValue,
      payday: paydayValue,
    })
  }
  const preventClose = (e: Event) => {
    e.preventDefault()
  }

  const [show, setShow] = useState(false);

  return (
    <Dialog open={activeModal === 'onboarding'} onOpenChange={() => {}}>
      <DialogContent
        className="sm:max-w-[425px]"
        onPointerDownOutside={preventClose}
        onEscapeKeyDown={preventClose}
        onInteractOutside={preventClose}
        showCloseButton={false}
      >
        <DialogHeader>
          <DialogTitle>Bem-vindo ao SoFiA</DialogTitle>
          <DialogDescription>
            Para começar, precisamos saber como te chamar.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 py-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Seu Nome
            </Label>
            <Input
              id="name"
              placeholder="Como gostaria de ser chamado?"
              {...register('name')}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>


          <div className="space-y-2">
            <Label htmlFor="salary" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Salário Mensal
            </Label>
            <Input
              id="salary"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="Ex: 5000"
              {...register('salary')}
            />
            {errors.salary && (
              <p className="text-sm text-destructive">{errors.salary.message}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Opcional. Nos ajuda a fornecer insights melhores.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="payday" className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Dia de Recebimento
            </Label>
            <Input
              id="payday"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="Ex: 5"
              {...register('payday')}
            />
            {errors.payday && (
              <p className="text-sm text-destructive">{errors.payday.message}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Dia do mês em que você recebe seu salário.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="api_key" className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              Chave de API do Gemini
            </Label>
            <div className='flex gap-2'>
              <Input
                id="api_key"
                type={show ? 'text' : 'password'}
                placeholder="sk-..."
                {...register('api_key')}
              />
              <Button
                type="button"
                onClick={() => setShow(!show)}
                className="bg-muted hover:bg-muted/80"
                disabled={isPending}
              >
                {show ? <EyeOff className="w-4 h-4 text-muted-foreground" /> : <Eye className="w-4 h-4 text-muted-foreground" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Você pode configurar isso mais tarde nos ajustes.
            </p>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? 'Criando perfil...' : 'Começar a usar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
