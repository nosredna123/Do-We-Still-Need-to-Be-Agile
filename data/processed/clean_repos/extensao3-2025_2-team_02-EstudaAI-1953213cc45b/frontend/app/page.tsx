'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Background } from './components/background/background'
import { FormEvent } from 'react'
import { useRouter } from 'next/navigation'

export default function Login() {
  const router = useRouter()
  const [credenciais, setCredenciais] = useState({
    email: '',
    senha: ''
  })
  const [erro, setErro] = useState('')
  const [entrando, setEntrando] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setEntrando(true)
    setErro('')
    try {
      const response = await fetch('http://localhost:8080/users/login', {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json',
        },
           body: JSON.stringify({
        email: credenciais.email,
        password: credenciais.senha,
      }),
    });

      const data = await response.json(); 
    if (data.error) {
      throw new Error(data.error || 'Erro ao fazer login.');
    }
    localStorage.setItem('accessToken', data.accessToken)
    console.log('Seja bem-vindo', data);
    router.push('/homepage'); //deve ir dps do login pra home 
    
  } catch (error) {
    console.error('Erro no login:', error);
    setErro(error instanceof Error ? error.message : 'Erro ao fazer login. Tente novamente.');
  } finally {  
    setEntrando(false)
  }
}

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCredenciais(prev => ({
      ...prev,
      [name]: value
    }))
    if (erro) setErro('')
  }

  return (
    <Background>
      <main className="w-full max-w-md flex flex-col justify-center items-center mx-auto h-full">
        <div className="mb-8 w-full">
          <h2 className="text-[#494949] text-4xl font-bold text-center mb-16">
            Login
          </h2>
          
          <form onSubmit={handleSubmit}>
            {erro && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 text-sm">
                {erro}
              </div>
            )}
            
            <input 
              type="email" 
              name="email"
              placeholder="E-mail" 
              value={credenciais.email}
              onChange={handleChange}
              className="text-[#494949] w-full border-2 border-[#818181] rounded-lg px-4 py-3 mb-6 focus:outline-none focus:border-[#494949]"
              required
            />
            
            <input 
              type="password" 
              name="senha"
              placeholder="Senha" 
              value={credenciais.senha}
              onChange={handleChange}
              className="text-[#494949] w-full border-2 border-[#818181] rounded-lg px-4 py-3 mb-8 focus:outline-none focus:border-[#494949]"
              required
            />
            
            <button 
              type="submit"
              disabled={entrando}
              className="w-full bg-[#098842] text-white rounded-lg px-4 py-3 font-bold border border-[#3B3434] hover:bg-[#087c3a] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {entrando ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
        </div>

        <div className="text-center w-full">
          <p className="text-[#494949] text-sm">
            Ainda não possui uma conta?{' '}
            <Link href="/cadastro" className="text-[#098842] font-bold hover:text-[#087c3a] transition-colors">
              Cadastre-se
            </Link>
          </p>
        </div>
      </main>
    </Background>
  )
}

