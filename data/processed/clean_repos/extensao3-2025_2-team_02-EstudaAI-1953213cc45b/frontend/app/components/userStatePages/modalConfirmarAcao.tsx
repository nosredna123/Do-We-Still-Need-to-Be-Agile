'use client';
import Image from "next/image";
import { useEffect } from 'react';

type ModalConfirmacaoProps = {
  isOpen: boolean;
  titulo: string;
  mensagem: string;
  onConfirmar: () => void;
  onCancelar: () => void;
  loading?: boolean;
}

export default function ModalConfirmacao({
  isOpen,
  titulo,
  mensagem,
  onConfirmar,
  onCancelar,
  loading = false
}: ModalConfirmacaoProps) {
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onCancelar();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onCancelar]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">

      <div 
        className="absolute inset-0 bg-black opacity-75"
        onClick={onCancelar}
        aria-hidden="true"
      />
      

      <div className="relative z-50 flex flex-col w-[90vw] max-w-[500px] bg-[#F5F5F5] rounded-xl overflow-hidden shadow-2xl mx-4">
        

        <div className="flex flex-row justify-between items-center px-6 py-4 bg-[#098842]">
          <h1 className="grow text-center font-montserrat font-bold text-white text-lg ml-6">
            {titulo}
          </h1>
          <button 
            className="w-6 h-6 cursor-pointer hover:opacity-70 transition-opacity flex items-center justify-center"
            onClick={onCancelar}
            aria-label="Fechar modal"
            disabled={loading}
          >
            <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar"/>
          </button>
        </div>


        <div className="grow p-6">
          <p className="font-montserrat font-normal text-[#494949] text-base leading-6 text-center">
            {mensagem}
          </p>
        </div>


        <div className="flex flex-row justify-center gap-4 px-6 py-4">
          <button 
            className="w-32 h-11 cursor-pointer bg-[#FF6262] rounded-lg hover:bg-[#e55555] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            onClick={onConfirmar}
            disabled={loading}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
            ) : (
              <p className="font-montserrat font-semibold text-white text-sm">
                Excluir
              </p>
            )}
          </button>
          
          <button 
            className="w-32 h-11 cursor-pointer bg-[#D9D9D9] rounded-lg hover:bg-[#c4c4c4] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={onCancelar}
            disabled={loading}
          >
            <p className="font-montserrat font-semibold text-[#444444] text-sm">
              Cancelar
            </p>
          </button>
        </div>
      </div>
    </div>
  );
}