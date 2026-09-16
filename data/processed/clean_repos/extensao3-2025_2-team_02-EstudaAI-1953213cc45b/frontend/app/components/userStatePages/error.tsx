'use client';

export default function ErrorPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] bg-white overflow-hidden">
      <div className="flex flex-col items-center gap-6 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
          <svg 
            className="w-8 h-8 text-red-500" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
        </div>
        
        <div className="space-y-2">
          <h2 className="font-montserrat font-bold text-xl text-red-600">
            Ocorreu um erro
          </h2>
          <p className="font-montserrat text-[#686464] max-w-md">
            Não foi possível carregar o conteúdo solicitado. 
            Por favor, tente novamente mais tarde.
          </p>
        </div>

        <button 
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-[#098842] text-white font-montserrat rounded-lg hover:bg-[#086B34] transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    </div>
  );
}