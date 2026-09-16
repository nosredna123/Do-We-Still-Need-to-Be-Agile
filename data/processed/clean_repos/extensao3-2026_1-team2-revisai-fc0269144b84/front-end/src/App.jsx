import { Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import GerarFlashcards from "./pages/GerarFlashcards";
import MyCards from "./pages/MyCards";
import DeckDetail from "./pages/DeckDetail";
import Weeks from "./pages/Weeks";
import MeusResumos from "./pages/MeusResumos";
import MeusDicionarios from "./pages/MeusDicionarios";
import Perfil from "./pages/Perfil";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/gerar" element={<GerarFlashcards />} />
      <Route path="/dashboard" element={<Navigate to="/gerar" replace />} />
      <Route path="/weeks" element={<Weeks />} />

      <Route path="/meus-cards" element={<MyCards />} />
      <Route path="/meus-cards/:deckId" element={<DeckDetail />} />
      <Route path="/resumos" element={<MeusResumos />} />
      <Route path="/dicionarios" element={<MeusDicionarios />} />
      <Route path="/perfil" element={<Perfil />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
