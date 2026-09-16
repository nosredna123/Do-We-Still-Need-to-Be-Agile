'use client';
import Image from "next/image";
import { useCallback, useEffect, useState, useRef } from 'react';
import LoadingPage from "../../components/userStatePages/loading"
import ErrorPage from "../../components/userStatePages/error"
import ModalConfirmacao from "../../components/userStatePages/modalConfirmarAcao"; 
import { Navbar } from "../../components/navbar";
import { useParams, useSearchParams } from 'next/navigation';

type TopicoData = {
  id: number;
  content: string;
  title: string;
  topic_id: number;
}

type MaterialDocumento = {
  id: number;
  public_url: string;
}

type MensagemAPI = {
  id: number;
  created_at: string;
  userId: number | null;
  topic_id: number;
  content: string;
}

type Mensagem = {
  id: number;
  conteudo: string;
  tempo: string;
  ia: boolean;
}

type Chat = {
  id: number;
  mensagens: Mensagem[];
}

type TopicoCompletoData = {
  topicos: TopicoData[];
  materiais: MaterialDocumento[];
  tituloTopico?: string;
}

type LLMResponse = {
  resposta: string;
}

const renderizarTextoComNegrito = (texto: string) => {
  if (!texto) return texto;
  
  const partes = texto.split(/(\*\*.*?\*\*)/g);
  
  return partes.map((parte, index) => {
    if (parte.startsWith('**') && parte.endsWith('**')) {
      const textoNegrito = parte.slice(2, -2);
      return <strong key={index}>{textoNegrito}</strong>;
    }
    return parte;
  });
};

export default function Page() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensagem, setMensagem] = useState('');
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [conteudoTemp, setConteudoTemp] = useState('');
  const [tituloTemp, setTituloTemp] = useState('');
  const [modalDelecaoAberto, setModalDelecaoAberto] = useState(false);
  const [topicoParaDeletar, setTopicoParaDeletar] = useState<TopicoData | null>(null);
  const [chatProcessando, setChatProcessando] = useState(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  const [topicoCompleto, setTopicoCompleto] = useState<TopicoCompletoData>({
    topicos: [],
    materiais: [],
    tituloTopico: ''
  });

  const [chat, setChat] = useState<Chat>({
    id: 0,
    mensagens: []
  });

  const handleAdicionarMaterial = useCallback(() => {
    console.log('Botão: Adicionar Novo Material');
    alert('Funcionalidade de adicionar novo material será implementada aqui');
  }, []);

  const handleAbrirMaterial = useCallback((material: MaterialDocumento) => {
    try {
      const token = localStorage.getItem('accessToken');
      let url = material.public_url;
      
      if (token && url.includes('supabase.co')) {
        url = `${url}?token=${token}`;
      }
      
      window.open(url, '_blank', 'noopener,noreferrer');
      
    } catch (err) {
      console.error('Erro ao abrir material:', err);
      alert('Erro ao abrir material. Tente novamente.');
    }
  }, []);

  const scrollToBottom = useCallback(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chat.mensagens, scrollToBottom]);

  const handleIniciarEdicao = useCallback((topico: TopicoData) => {
    setEditandoId(topico.id);
    setTituloTemp(topico.title);
    setConteudoTemp(topico.content);
  }, []);

  const handleSalvarEdicao = useCallback(async (id: number) => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('accessToken');
      
      const response = await fetch(`http://localhost:8080/students/topic/summaries/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: tituloTemp,
          content: conteudoTemp,
        }),
      });

      if (!response.ok) throw new Error('Erro ao salvar edição');

      setTopicoCompleto(prev => ({
        ...prev,
        topicos: prev.topicos.map(topico =>
          topico.id === id
            ? { ...topico, title: tituloTemp, content: conteudoTemp }
            : topico
        )
      }));

      setEditandoId(null);
      console.log('Edição salva com sucesso!');

    } catch (err) {
      console.error('Erro ao salvar edição:', err);
      alert('Erro ao salvar edição. Tente novamente.');
    } finally {
      setLoading(false);
    }
  }, [tituloTemp, conteudoTemp]);

  const handleCancelarEdicao = useCallback(() => {
    setEditandoId(null);
    setTituloTemp('');
    setConteudoTemp('');
  }, []);

  const handleAbrirModalDelecao = useCallback((topico: TopicoData) => {
    setTopicoParaDeletar(topico);
    setModalDelecaoAberto(true);
  }, []);

  const handleConfirmarDelecao = useCallback(async () => {
    if (!topicoParaDeletar) return;

    try {
      setLoading(true);
      
      const token = localStorage.getItem('accessToken');
      
      const response = await fetch(`http://localhost:8080/students/topic/summaries/${topicoParaDeletar.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Erro ao deletar tópico');

      setTopicoCompleto(prev => ({
        ...prev,
        topicos: prev.topicos.filter(topico => topico.id !== topicoParaDeletar.id)
      }));

      console.log('Tópico deletado com sucesso!');
      
    } catch (err) {
      console.error('Erro ao deletar tópico:', err);
      alert('Erro ao deletar tópico. Tente novamente.');
    } finally {
      setLoading(false);
      setModalDelecaoAberto(false);
      setTopicoParaDeletar(null);
    }
  }, [topicoParaDeletar]);

  const handleCancelarDelecao = useCallback(() => {
    setModalDelecaoAberto(false);
    setTopicoParaDeletar(null);
  }, []);

  const handleAtualizarTranscricao = useCallback(() => {
    console.log('Botão: Atualizar Transcrição');
  }, []);

  const handleEnviarMensagem = useCallback(async () => {
    if (!mensagem.trim() || chatProcessando) return;

    const token = localStorage.getItem('accessToken');
    if (!token) {
      alert('Usuário não autenticado');
      return;
    }

    const topicId = searchParams.get('topicId') || id;
    if (!topicId) {
      alert('ID do tópico não encontrado');
      return;
    }

    const novaMensagemUsuario: Mensagem = {
      id: Date.now(),
      conteudo: mensagem.trim(),
      tempo: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
      ia: false
    };

    setChat(prev => ({
      ...prev,
      mensagens: [...prev.mensagens, novaMensagemUsuario]
    }));

    const mensagemOriginal = mensagem.trim();
    setMensagem('');
    setChatProcessando(true);

    try {
      await fetch(`http://localhost:8080/students/topic/messages?topicId=${topicId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: mensagemOriginal
        })
      });

      const llmResponse = await fetch(`http://localhost:8080/students/llm/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: mensagemOriginal,
          topicId: parseInt(topicId.toString())
        })
      });

      if (!llmResponse.ok) throw new Error('Erro ao obter resposta da IA');

      const data: LLMResponse = await llmResponse.json();

      const novaRespostaIA: Mensagem = {
        id: Date.now() + 1,
        conteudo: data.resposta,
        tempo: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        ia: true
      };

      setChat(prev => ({
        ...prev,
        mensagens: [...prev.mensagens, novaRespostaIA]
      }));

    } catch (err) {
      console.error('Erro:', err);
      alert(err instanceof Error ? err.message : 'Erro ao processar mensagem');
    } finally {
      setChatProcessando(false);
    }
  }, [mensagem, chatProcessando, searchParams, id]);

  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!chatProcessando) {
      setMensagem(event.target.value);
    }
  }, [chatProcessando]);

  const handleKeyPress = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && mensagem.trim() && !chatProcessando) {
      handleEnviarMensagem();
    }
  }, [mensagem, chatProcessando, handleEnviarMensagem]);

  const fetchMensagensChat = useCallback(async (topicId: string, token: string) => {
    try {
      const response = await fetch(
        `http://localhost:8080/students/topic/messages?topicId=${topicId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error("Failed to fetch messages");

      const mensagensAPI: MensagemAPI[] = await response.json();
      
      const mensagensConvertidas: Mensagem[] = mensagensAPI.map(msg => ({
        id: msg.id,
        conteudo: msg.content,
        tempo: new Date(msg.created_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        ia: msg.userId === null
      }));

      setChat(prev => ({
        ...prev,
        mensagens: mensagensConvertidas
      }));

    } catch (err) {
      console.error('Erro ao carregar mensagens do chat:', err);
    }
  }, []);

  useEffect(() => {
    const topicId = searchParams.get('topicId') || id;
    const token = localStorage.getItem('accessToken');

    if (!topicId || !token) return;

    let mounted = true;

    const fetchTopicData = async () => {
      if (!mounted) return;
      
      try {
        setLoading(true);
        setError(null);

        const headers = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        };

        const [materialsResponse, summariesResponse] = await Promise.all([
          fetch(`http://localhost:8080/students/topic/materials?topicId=${topicId}`, {
            method: 'GET',
            headers
          }),
          fetch(`http://localhost:8080/students/topic/summaries?topicId=${topicId}`, {
            method: 'GET',
            headers
          })
        ]);

        if (!materialsResponse.ok) {
          throw new Error("Failed to fetch materials");
        }

        if (!summariesResponse.ok) {
          throw new Error("Failed to fetch summaries");
        }

        const [materiais, topicos] = await Promise.all([
          materialsResponse.json(),
          summariesResponse.json()
        ]);

        if (mounted) {
          setTopicoCompleto({
            topicos: topicos.summaries || [],
            materiais: materiais || [],
            tituloTopico: topicos.title
          });

          await fetchMensagensChat(topicId.toString(), token);
        }

      } catch (err) {
        if (mounted) {
          if (err instanceof Error){
            setError(err.message);
          } else {
            setError('Erro desconhecido ao carregar dados');
          }
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchTopicData();

    return () => {
      mounted = false;
    };
  }, [searchParams, id]); 

  return(
    <main className="bg-[#FFFFFF]">
      <Navbar />
      
      <ModalConfirmacao
        isOpen={modalDelecaoAberto}
        titulo="Excluir Tópico"
        mensagem={`Tem certeza que deseja excluir "${topicoParaDeletar?.title}"? Esta ação não pode ser desfeita.`}
        onConfirmar={handleConfirmarDelecao}
        onCancelar={handleCancelarDelecao}
        loading={loading}
      />

      {loading ? (
        <LoadingPage />
      ) : error ? (
        <ErrorPage />
      ) : (
        <div className="flex min-h-[calc(100vh-4rem)] max-h-[calc(100vh-4rem)] gap-4 bg-white w-full p-4 box-border">
          <section className="overflow-y-auto flex flex-col flex-1 gap-4 border-2 border-[#098842] bg-white rounded-xl p-4 max-h-[calc(100vh-6rem)] w-7/10 drop-shadow-md">
            <h1 className="font-montserrat font-bold text-[#686464] text-center m-0 pt-2 text-2xl">
              {topicoCompleto.tituloTopico || 'Tópico'}
            </h1> 

            <div className="flex flex-col pl-2 pr-3 pt-2 pb-3 border-[1.5px] border-[#098842] rounded-2xl bg-[#F5F5F5]">
              <span className="flex justify-between items-center mb-2 px-0.5 py-0.5">
                <h2 className="font-montserrat font-bold text-[#494949] text-left mb-2 text-lg">
                  Material Original
                </h2>
              </span>

              <div className="flex flex-row gap-2 overflow-x-auto py-2
                [&::-webkit-scrollbar]:h-1.5
                [&::-webkit-scrollbar-track]:bg-gray-100
                [&::-webkit-scrollbar-track]:rounded
                [&::-webkit-scrollbar-thumb]:bg-[#098842]
                [&::-webkit-scrollbar-thumb]:rounded">
                
                {/*<button 
                  className="flex flex-col justify-center items-center min-w-36 min-h-20 pt-3 ml-2 mb-2 border-2 border-dashed border-[#098842] rounded-xl shrink-0 bg-white hover:bg-[#f0f8f0] transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#098842] focus:ring-opacity-50 group"
                  onClick={handleAdicionarMaterial}
                  aria-label="Adicionar novo material"
                >
                  <Image 
                    src="/imagens/add.svg" 
                    width={24} 
                    height={24} 
                    className="group-hover:scale-110 transition-transform" 
                    alt="Adicionar material"
                  />
                  <span className="font-montserrat font-normal text-[0.7rem] text-center text-[#098842] mx-0.5 px-1 mt-1">
                    Adicionar Material
                  </span>
                </button>*/}
                
                {topicoCompleto.materiais.map(material => (
                  <button 
                    key={material.id} 
                    className="flex grow-0 flex-col justify-around items-center min-w-36 min-h-20 max-w-36 max-h-20 pt-3 ml-2 mb-2 border-[1.5px] border-[#098842] rounded-xl shrink-0 bg-[#F5F5F5] hover:bg-[#e8f5e8] transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#098842] focus:ring-opacity-50"
                    onClick={() => handleAbrirMaterial(material)}
                    disabled={loading}
                    aria-label={`Abrir material ${material.id}`}
                  >
                    <Image 
                      src="/imagens/file.svg" 
                      width={36} 
                      height={20} 
                      className="mx-14" 
                      alt={`Ícone do material`}
                    />
                    <span className="font-montserrat font-normal text-[0.7rem] text-center text-[#098842] mx-0.5 px-1 w-full truncate">
                      {material.public_url.split('/').pop() || `Material ${material.id}`}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {topicoCompleto.topicos.map(topico => (
              <div key={topico.id} className="flex-1 pr-3 pl-2 pt-2 pb-3 border-[1.5px] border-[#098842] rounded-2xl bg-[#F5F5F5] text-black">
                <span className="flex justify-between items-center mb-2 px-0.5 py-0.5">
                  {editandoId === topico.id ? (
                    <input
                      type="text"
                      value={tituloTemp}
                      onChange={(e) => setTituloTemp(e.target.value)}
                      className="font-montserrat font-bold text-[#494949] text-left mb-2 text-lg bg-transparent border-b border-[#098842] focus:outline-none w-full"
                      autoFocus
                    />
                  ) : (
                    <h2 className="font-montserrat font-bold text-[#494949] text-left mb-2 text-lg">
                      {topico.title}
                    </h2>
                  )}
                  <div className="flex gap-2">
                    {editandoId === topico.id ? (
                      <>
                        <button 
                          className="w-5 h-5 cursor-pointer hover:opacity-70 transition-opacity" 
                          aria-label="Salvar edição"
                          onClick={() => handleSalvarEdicao(topico.id)}
                        >
                          <Image src="/imagens/check.svg" width={20} height={20} alt="Salvar"/>
                        </button>
                        {/*<button 
                          className="w-5 h-5 cursor-pointer hover:opacity-70 transition-opacity" 
                          aria-label="Cancelar edição"
                          onClick={handleCancelarEdicao}
                        >
                          <Image src="/imagens/X-pequeno.svg" width={20} height={20} alt="Cancelar"/>
                        </button>*/}
                      </>
                    ) : 
                    <></>
                      /*<>
                        <button 
                          className="w-5 h-5 cursor-pointer hover:opacity-70 transition-opacity" 
                          aria-label="Excluir tópico"
                          onClick={() => handleAbrirModalDelecao(topico)}
                        >
                          <Image src="/imagens/X-pequeno.svg" width={20} height={20} alt="Excluir"/>
                        </button>
                      </>*/
                    }
                  </div>
                </span>
                
                {editandoId === topico.id ? (
                  <textarea
                    value={conteudoTemp}
                    onChange={(e) => setConteudoTemp(e.target.value)}
                    className="font-montserrat font-normal text-[#494949] text-left leading-6 m-0 w-full h-64 p-2 border border-[#098842] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#098842]"
                  />
                ) : (
                  <div className="font-montserrat font-normal text-[#494949] text-left leading-6 m-0 text-clamp-1">
                    {renderizarTextoComNegrito(topico.content)}
                  </div>
                )}
                
                {editandoId !== topico.id && (
                  <span className="flex flex-row justify-end gap-5 px-0.5 py-0.5 mt-4">
                    {/*<button 
                      className="w-5 h-5 cursor-pointer hover:opacity-70 transition-opacity" 
                      aria-label="Atualizar"
                      onClick={handleAtualizarTranscricao}
                    >
                      <Image src="/imagens/refresh.svg" width={20} height={20} alt="Atualizar"/>
                    </button>
                    <button 
                      className="w-5 h-5 cursor-pointer hover:opacity-70 transition-opacity" 
                      aria-label="Editar"
                      onClick={() => handleIniciarEdicao(topico)}
                    >
                      <Image src="/imagens/editar.svg" width={20} height={20} alt="Editar"/>
                    </button>*/}
                  </span>
                )}
              </div>
            ))}
          </section>

          <section className="flex flex-col w-3/10 min-w-72 gap-3 ">
            <div 
              ref={chatContainerRef}
              className="flex-1 border-2 border-[#098842] bg-white rounded-xl min-h-86 p-4 overflow-y-auto flex flex-col gap-4 box-border drop-shadow-md"
            >
              {chat.mensagens.map(mensagem => ( 
                <div key={mensagem.id} className={mensagem.ia ? "self-start max-w-100 p-3 bg-white border-2 border-[#098842] rounded-2xl text-[#333333] font-montserrat text-sm leading-6 relative box-border" : "self-end max-w-80 p-3 bg-[#098842] rounded-2xl text-white font-montserrat text-sm leading-6 relative box-border"}>
                  <div className="font-montserrat text-sm leading-6">
                    {renderizarTextoComNegrito(mensagem.conteudo)}
                  </div>
                  <div className="text-[0.7rem] opacity-80 mt-1 text-right">{mensagem.tempo}</div>
                </div>
              ))}
            </div>

            <div className="flex items-center h-12 border-2 border-[#098842] bg-white rounded-xl px-4 gap-2 box-border drop-shadow-md">
              <button 
                className="w-6 h-6 cursor-pointer" 
                aria-label="Enviar mensagem"
                onClick={handleEnviarMensagem}
                disabled={!mensagem.trim() || chatProcessando}
              >
                <Image src="/imagens/send.svg" width={24} height={24} alt="Enviar"/>
              </button>
              <input
                type="text"
                value={mensagem}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder={chatProcessando ? "IA está respondendo..." : "Faça uma pergunta"}
                className="font-montserrat font-normal text-[#494949] p-2 flex-1 bg-transparent border-none outline-none box-border placeholder:text-[#989898] placeholder:italic"
                aria-label="Digite sua pergunta"
                disabled={chatProcessando}
              />
            </div>
          </section>
        </div>
      )}
    </main>
  );
}