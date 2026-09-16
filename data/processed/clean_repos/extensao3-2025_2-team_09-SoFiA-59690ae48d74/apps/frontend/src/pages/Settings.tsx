import { Separator } from '@/components/ui/separator'
import { Loader2 } from 'lucide-react'
import { ProfileForm } from '@/features/profile/components/profile-form'
import { useProfile } from '@/features/profile/hooks/useProfile.ts'
import { Label } from '@/components/ui/label.tsx'
import { Card, CardTitle } from '@/components/ui/card.tsx'
import { useThemeStore } from '@/stores/themeStore'

const Setting = () => {
  const { user, form, onSubmit, isPending, memberSince } = useProfile()
  if (!user) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const { theme, setTheme } = useThemeStore();

  return (
    <div className="p-8 max-w-4xl mx-auto animate-in fade-in duration-500">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Ajustes</h1>
          <p className="text-muted-foreground">
            Gerencie suas informações pessoais e configurações.
          </p>
        </div>
        <Separator />
        <p>Informações pessoais</p>
        <ProfileForm
          user={user}
          form={form}
          onSubmit={onSubmit}
          isPending={isPending}
          memberSince={memberSince}
        />
        <p>Aparência</p>
        <Card className='p-6'>
            <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Tema</Label>
              <p className="text-sm text-muted-foreground">
              Escolha o tema da aplicação
              </p>
            </div>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
              className="px-3 py-2 rounded-md border border-input bg-background text-sm"
            >
              <option value="light">Claro</option>
              <option value="dark">Escuro</option>
              <option value="system">Padrão do Dispositivo</option>
            </select>
            </div>
        </Card>
      </div>
    </div>
  )
}

export default Setting
