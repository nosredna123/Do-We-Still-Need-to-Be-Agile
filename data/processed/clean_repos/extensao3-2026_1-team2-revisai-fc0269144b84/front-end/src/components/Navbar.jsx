import { Link } from "react-router-dom";
import robotIcon from "../assets/chatbot.png";

export default function Navbar() {
  return (
    <nav className="w-full flex items-center justify-between px-8 py-4 bg-[#f5f5ec] border-b border-gray-200">
      <Link to="/" className="flex items-center gap-2 font-bold text-gray-800 text-lg">
        <img src={robotIcon} alt="Logo" className="w-8 h-8" /> REVISAI
      </Link>
      <div className="flex items-center gap-4">
        <Link
          to="/login"
          className="bg-[#2d6a4f] text-white px-5 py-2 rounded-lg font-medium hover:bg-[#1b4332] transition"
        >
          Entrar
        </Link>
      </div>
    </nav>
  );
}