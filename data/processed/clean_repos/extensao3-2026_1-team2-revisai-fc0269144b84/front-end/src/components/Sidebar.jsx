import { useNavigate, useLocation } from "react-router-dom";
import robotIcon from "../assets/chatbot.png";
import { User, Calendar, CreditCard, Bot, FileText, BookOpen } from "lucide-react";
import { useFlashcards } from "../contexts/FlashcardContext";

const navItems = [
  {
    label: "Perfil",
    path: "/perfil",
    icon: <User className="mr-2 h-5 w-5" />
  },
  {
    label: "Semanas",
    path: "/weeks",
    icon: <Calendar className="mr-2 h-5 w-5" />
  },
  {
    label: "Meus Cards",
    path: "/meus-cards",
    icon: <CreditCard className="mr-2 h-5 w-5" />
  },
  {
    label: "Meus Resumos",
    path: "/resumos",
    icon: <FileText className="mr-2 h-5 w-5" />
  },
  {
    label: "Meus Dicionários",
    path: "/dicionarios",
    icon: <BookOpen className="mr-2 h-5 w-5" />
  },
  {
    label: "Gerar",
    path: "/gerar",
    icon: <Bot className="mr-2 h-5 w-5" />
  },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { themes, resumos, dicionarios } = useFlashcards();

  const cardsCount = themes.reduce((acc, t) => acc + t.cards.length, 0);
  const resumosCount = resumos.length;
  const dicionariosCount = dicionarios.length;

  const counts = {
    "Meus Cards": cardsCount,
    "Meus Resumos": resumosCount,
    "Meus Dicionários": dicionariosCount,
  };

  return (
    <aside
      style={{ width: 256, flexShrink: 0, display: "flex", flexDirection: "column" }}
      className="bg-sidebar-background text-sidebar-foreground"
    >
      <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-auto pt-4">
        {/* Logo */}
        <div
          className="flex justify-center mb-6 px-2 cursor-pointer"
          onClick={() => navigate("/")}
        >
          <img src={robotIcon} alt="RevisAI Logo" style={{ width: 64, height: 64 }} />
        </div>
        <p className="text-center text-sm font-bold text-sidebar-foreground mb-6 tracking-wide">REVISAI</p>

        {/* Nav */}
        <div className="relative flex w-full min-w-0 flex-col p-2">
          <div className="w-full text-sm">
            <ul className="flex w-full min-w-0 flex-col gap-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                const count = counts[item.label] ?? 0;

                return (
                  <li key={item.label} className="relative">
                    <button
                      onClick={() => navigate(item.path)}
                      className={`flex w-full items-center gap-2 overflow-hidden rounded-md p-2 text-left outline-none ring-sidebar-ring transition-[width,height,padding] focus-visible:ring-2 active:bg-sidebar-accent active:text-sidebar-accent-foreground disabled:pointer-events-none disabled:opacity-50 hover:text-sidebar-accent-foreground h-8 text-sm hover:bg-sidebar-accent/50 [&>svg]:shrink-0
                        ${isActive
                          ? "bg-sidebar-accent text-sidebar-accent-foreground font-semibold"
                          : ""
                        }`}
                    >
                      {item.icon}
                      <span>{item.label}</span>
                      {count > 0 && (
                        <span className="ml-auto bg-white text-sidebar-background text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                          {count}
                        </span>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>

      {/* User avatar bottom */}
      <div className="px-4 py-5 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white text-xs font-bold">
          U
        </div>
        <div>
          <p className="text-white text-xs font-semibold">Usuário</p>
          <p className="text-white/40 text-[11px]">Plano grátis</p>
        </div>
      </div>
    </aside>
  );
}
