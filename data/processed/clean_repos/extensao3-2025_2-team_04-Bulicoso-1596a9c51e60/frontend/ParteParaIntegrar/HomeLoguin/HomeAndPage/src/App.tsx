import { useState } from "react";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
// Importamos o serviço de API que criamos
import { api } from "./services/api";

export default function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'login'>('home');

  const handleNavigation = (page: 'home' | 'login') => {
    setCurrentPage(page);
  };

  const handleGoogleLogin = () => {
    // Chama a função do api.js que faz o redirecionamento.
    // O navegador sairá desta página e irá para o Google.
    // Não adianta colocar setCurrentPage('home') aqui, pois a página será recarregada.
    api.loginGoogle();
  };

  return (
    <>
      {currentPage === 'home' ? (
        <div className="w-[1920px] h-[2062px] overflow-auto">
          <HomePage onNavigate={handleNavigation} />
        </div>
      ) : (
        <div className="w-screen h-screen overflow-hidden">
          <LoginPage onGoogleLogin={handleGoogleLogin} />
        </div>
      )}
    </>
  );
}