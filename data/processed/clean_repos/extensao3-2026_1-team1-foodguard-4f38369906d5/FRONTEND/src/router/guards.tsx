import { Navigate, Outlet, useParams } from "react-router-dom";
import Index from "@/pages/Index";
import Galeria from "@/pages/Galeria";
import Landing from "@/pages/Landing";
import { useAuth } from "@/hooks/use-auth";

// Landing pública ("/"): usuário logado vai à galeria; visitante vê a landing.
export const LandingRoute = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/galeria" replace /> : <Landing />;
};

// Rotas só para visitantes (RN007): usuário logado é redirecionado à galeria
export const GuestOnlyRoute = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/galeria" replace /> : <Outlet />;
};

// Rotas protegidas (RN007): exige sessão ativa
export const ProtectedRoute = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

// Gate de anamnese (RN001): acesso à galeria exige anamnese completa
export const GalleryRoute = () => {
  const { hasAnamnese } = useAuth();
  return hasAnamnese ? <Galeria /> : <Navigate to="/anamnese" replace />;
};

// Gate de anamnese (RN001): acesso ao chat exige anamnese completa.
// `chatId` (opcional) abre uma conversa específica vinda da galeria.
export const ChatRoute = () => {
  const { hasAnamnese } = useAuth();
  const { chatId } = useParams();
  return hasAnamnese ? (
    <Index initialChatId={chatId ?? null} />
  ) : (
    <Navigate to="/anamnese" replace />
  );
};
