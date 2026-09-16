import React from "react";
// O useNavigate não é necessário aqui, pois a navegação inicial é externa (vai para o Google)
// import { useNavigate } from "react-router-dom";

// Importe o seu componente de página de login (ajuste o caminho se necessário)
import LoginPage from "../ParteParaIntegrar/HomeLoguin/HomeAndPage/src/pages/LoginPage";

// Importe a API que criamos para chamar a função de login
import { api } from "./services/api";

export default function LoginWrapper() {

  const handleGoogleLogin = () => {
    // 1. O usuário clica no botão de login com Google.
    // 2. Chamamos api.loginGoogle().
    // 3. A função muda o window.location.href para http://127.0.0.1:8000/auth/login.
    // 4. O navegador sai do React e vai para o seu Backend -> Google.
    api.loginGoogle();
  };

  return <LoginPage onGoogleLogin={handleGoogleLogin} />;
}