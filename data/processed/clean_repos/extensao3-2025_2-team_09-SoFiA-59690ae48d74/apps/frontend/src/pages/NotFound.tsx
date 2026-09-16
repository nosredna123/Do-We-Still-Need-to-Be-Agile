import { useLocation, Link } from 'react-router-dom'
import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Home, ArrowLeft } from 'lucide-react'

const NotFound = () => {
  const location = useLocation()

  useEffect(() => {
    console.error(
      '404 Error: User attempted to access non-existent route:',
      location.pathname
    )
  }, [location.pathname])

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30">
      <div className="text-center space-y-6 px-4">
        <div className="space-y-2">
          <h1 className="text-9xl font-bold text-primary">404</h1>
          <h2 className="text-3xl font-semibold">Página não encontrada</h2>
          <p className="text-xl text-muted-foreground max-w-md mx-auto">
            Desculpe, a página que você está procurando não existe ou foi
            movida.
          </p>
        </div>

        <div className="flex gap-4 justify-center pt-4">
          <Button asChild size="lg" className="gap-2">
            <Link to="/">
              <Home className="w-5 h-5" />
              Voltar ao Início
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="gap-2">
            <Link to="/chat">
              <ArrowLeft className="w-5 h-5" />
              Ir para o Chat
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
}

export default NotFound
