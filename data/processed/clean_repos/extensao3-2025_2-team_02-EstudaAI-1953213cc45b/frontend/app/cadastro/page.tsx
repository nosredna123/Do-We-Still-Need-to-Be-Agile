'use client'

import Link from 'next/link'
import { Background } from '../components/background/background'
import { useState } from 'react'
import { FormEvent } from 'react'
import { useRouter } from 'next/navigation'

interface FormaCerta  {
  nome: string;
  email: string;
  senha: string; //tirei confirmar senha, pois não tem no back
}

interface FormaErrada {
  nome?: string;
  email?: string;
  senha?: string;
}

export default function Cadastro() {
  const router = useRouter()

  const [formaCerta, setFormaCerta] = useState<FormaCerta>({
    nome: '',
    email: '',
    senha: '',
  })
  
  const [formaErrada, setFormaErrada] = useState<FormaErrada>({})
  const [cadastrando, setCadastrando] = useState(false)

  const validainfo = (): boolean => {
    const erros: FormaErrada = {}

    if (!formaCerta.nome.trim()) {
      erros.nome = 'O nome é obrigatório.'
    }

    if (!formaCerta.email) {
      erros.email = 'O e-mail é obrigatório.'
    } else if (!/\S+@\S+\.\S+/.test(formaCerta.email)) {
      erros.email = 'O e-mail é inválido.'
    }

    if (!formaCerta.senha) {
      erros.senha = 'A senha é obrigatória.'
    } else if (formaCerta.senha.length < 8) {
      erros.senha = 'A senha deve ter pelo menos 8 caracteres.'
    }

    setFormaErrada(erros)
    return Object.keys(erros).length === 0
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormaCerta({
      ...formaCerta,
      [name]: value,
    })
    
    if (formaErrada[name as keyof FormaErrada]) {
      setFormaErrada({
        ...formaErrada,
        [name]: undefined,
      })
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validainfo()) {
      return
    }

    setCadastrando(true)

    try {
      console.log('Formulário enviado com sucesso:', formaCerta);
      const response = await fetch('http://localhost:8080/students/register', { //trocar para o endpoint correto da API
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formaCerta.nome,
          email: formaCerta.email,
          password: formaCerta.senha,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Erro ao cadastrar usuário.');
      }

      const data = await response.json();
      console.log('Cadastro bem-sucedido:', data);
      
      router.push('/'); //ja redireciona para login
    } catch (error) {
      console.error('Erro no cadastro:', error);
      setFormaErrada({ 
        email: error instanceof Error ? error.message : 'Erro ao realizar cadastro. Tente novamente.' 
      });
    } finally {
      setCadastrando(false);
    }
  };

  return (
    <Background>
      <main className="w-full max-w-md block flex-col justify-center items-center">
        <div className="mb-8 w-full">
          <h2 className="text-[#494949] text-4xl font-bold text-center mb-16">
            Cadastro
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <input 
                type="text" 
                name="nome"
                placeholder="Nome completo"
                value={formaCerta.nome}
                onChange={handleChange}
                className={`text-[#494949] w-full border-2 rounded-lg px-4 py-3 focus:outline-none ${
                  formaErrada.nome ? 'border-red-500' : 'border-[#494949] focus:border-[#494949]'
                }`}
              />
              {formaErrada.nome && (
                <p className="text-red-500 text-sm mt-1">{formaErrada.nome}</p>
              )}
            </div>
            
            <div className="mb-6">
              <input
                type="email"    
                name="email"
                placeholder="E-mail" 
                value={formaCerta.email}
                onChange={handleChange}
                className={`text-[#494949] w-full border-2 rounded-lg px-4 py-3 focus:outline-none ${
                  formaErrada.email ? 'border-red-500' : 'border-[#494949] focus:border-[#494949]'
                }`}
              />  
              {formaErrada.email && (
                <p className="text-red-500 text-sm mt-1 ">{formaErrada.email}</p>
              )}
            </div>
            
            <div className="mb-6">
              <input 
                type="password" 
                name="senha"
                placeholder="Senha" 
                value={formaCerta.senha}
                onChange={handleChange}
                className={`text-[#494949] w-full border-2 rounded-lg px-4 py-3 focus:outline-none ${
                  formaErrada.senha ? 'border-red-500' : 'border-[#494949] focus:border-[#494949]'
                }`}
              /> 
              {formaErrada.senha && (
                <p className="text-red-500 text-sm mt-1">{formaErrada.senha}</p>
              )}
            </div>
          
            {/* Configs do botão de Cadastrar */}
            <button 
              type="submit"
              disabled={cadastrando}
              className="w-full bg-[#098842] text-white rounded-lg px-4 py-3 font-montserrat font-bold border border-[#3B3434] hover:bg-[#087c3a] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {cadastrando ? 'Cadastrando...' : 'Cadastrar'}
            </button>
          </form>
        </div>
        
        <div className="text-center w-full">
          <p className="text-[#494949] text-sm font-montserrat">
            Já possui uma conta?{' '}
            <Link href="/" className="text-[#098842] font-bold hover:text-[#087c3a] transition-colors">
              Login
            </Link>
          </p>
        </div>
      </main>
    </Background>
  )
}
