"use client"

export default function UECEBotHome() {
  const handleStartChat = () => {
    console.log("Iniciar chat pressionado")
    // Aqui você pode navegar para a tela do chat
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Status bar simulada */}
      <div className="bg-white px-4 py-2 flex justify-between items-center text-sm font-medium">
        <span>9:41</span>
        <div className="flex items-center gap-1">
          <div className="flex gap-1">
            <div className="w-1 h-3 bg-black rounded-sm"></div>
            <div className="w-1 h-3 bg-black rounded-sm"></div>
            <div className="w-1 h-3 bg-black rounded-sm"></div>
            <div className="w-1 h-3 bg-gray-300 rounded-sm"></div>
          </div>
          <svg className="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M17.778 8.222c-4.296-4.296-11.26-4.296-15.556 0A1 1 0 01.808 6.808c5.076-5.077 13.308-5.077 18.384 0a1 1 0 01-1.414 1.414zM14.95 11.05a7 7 0 00-9.9 0 1 1 0 01-1.414-1.414 9 9 0 0112.728 0 1 1 0 01-1.414 1.414zM12.12 13.88a3 3 0 00-4.24 0 1 1 0 01-1.415-1.414 5 5 0 017.07 0 1 1 0 01-1.415 1.414zM9 16a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div className="w-6 h-3 border border-black rounded-sm">
            <div className="w-4 h-full bg-green-500 rounded-sm"></div>
          </div>
        </div>
      </div>

      {/* Barra verde superior */}
      <div className="h-16 bg-green-500"></div>

      {/* Conteúdo principal */}
      <div className="flex-1 flex flex-col justify-between items-center px-5 py-10">
        <div className="flex-1 flex flex-col justify-center items-center">
          <h1 className="text-2xl text-gray-600 text-center mb-1 font-light">Bem vindo ao</h1>
          <h2 className="text-3xl text-gray-800 text-center font-bold mb-10">UECEBot</h2>

          {/* Ícone/Logo do bot */}
          <div className="my-5">
          </div>
        </div>

        {/* Botão Iniciar Chat */}
        <button
          onClick={handleStartChat}
          className="bg-green-500 hover:bg-green-600 active:bg-green-700 text-white text-lg font-semibold py-4 px-16 rounded-full shadow-lg transition-colors duration-200 mb-5"
        >
          Iniciar chat
        </button>
      </div>

      {/* Navegação inferior simulada */}
      <div className="bg-white border-t border-gray-200 px-4 py-2 flex justify-between items-center">
        <button className="p-2">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button className="p-2">
          <div className="w-4 h-4 border-2 border-gray-400 rounded-sm"></div>
        </button>
        <button className="p-2">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}