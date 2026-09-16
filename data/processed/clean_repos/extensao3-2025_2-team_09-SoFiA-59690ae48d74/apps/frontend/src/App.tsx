import { Toaster } from '@/components/ui/toaster.tsx'
import { Toaster as Sonner } from '../src/components/ui/sonner'
import { TooltipProvider } from '@/components/ui/tooltip.tsx'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from '../src/components/Layout'
import Home from './pages/Home'
import Chat from '../src/pages/Chat'
import Setting from './pages/Settings'
import NotFound from '../src/pages/NotFound'
import { useAuthCheck } from '@/features/auth/hooks/useAuthCheck'
import { ModalLayer } from '@/components/ModalLayer.tsx'
import { useEffect } from 'react'
import { useThemeStore } from '@/stores/themeStore.ts'

const queryClient = new QueryClient()

const AppContent = () => {
  useAuthCheck()

  const { theme, setTheme } = useThemeStore();              

  useEffect(() => {
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;
    if (saved) setTheme(saved)
  }, [])

  return (
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <ModalLayer />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/chat/:sessionId" element={<Chat />} />
            <Route path="/settings" element={<Setting />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  )
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AppContent />
  </QueryClientProvider>
)

export default App
