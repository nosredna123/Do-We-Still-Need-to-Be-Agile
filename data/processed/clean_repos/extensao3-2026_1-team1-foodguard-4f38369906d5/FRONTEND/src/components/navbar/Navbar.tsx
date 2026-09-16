import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { FiUser } from "react-icons/fi"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import EditProfileModal from "@/components/profile/EditProfileModal"
import { useAuth } from "@/hooks/use-auth"
import { useToast } from "@/hooks/use-toast"

type NavBarProps = {
    variant?: "home" | "app"
}

const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" })
}

const NavBar = ({ variant = "home" }: NavBarProps) => {
    const navigate = useNavigate();
    const { logout, isAuthenticated } = useAuth();
    const { toast } = useToast();
    const [profileOpen, setProfileOpen] = useState(false);

    const handleLogout = async () => {
        try {
            await logout();
            toast({ description: "Você saiu da sua conta." });
            navigate("/", { replace: true });
        } catch (err) {
            console.error("Erro ao sair:", err);
        }
    };

    return (
        <header className={variant === "home" ? "fixed pt-6 left-1/2 z-50 w-[min(95%,1100px)] -translate-x-1/2" : "pt-6"}>
            <div className="flex items-center gap-4">
                <div className="flex flex-1 items-center justify-between rounded-full border border-zinc-500 bg-white pl-6 pr-8 py-3 shadow-sm shadow-black/15 backdrop-blur-md">
                    <button
                        onClick={() => variant === "home"
                            ? window.scrollTo({ top: 0, behavior: "smooth" })
                            : navigate("/galeria")
                        }
                        className="font-sansita text-4xl font-extrabold tracking-tight text-black"
                    >
                        FoodGuard
                    </button>

                    <nav className="flex items-center gap-16">
                        {variant === "home" ? (
                            <>
                                <button
                                    onClick={() => scrollTo("como-funciona")}
                                    className="text-base font-semibold text-black transition-colors hover:text-foodguard-500"
                                >
                                    Como funciona?
                                </button>
                                <button
                                    onClick={() => scrollTo("quem-somos")}
                                    className="text-base font-semibold text-black transition-colors hover:text-foodguard-500"
                                >
                                    Quem somos
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => navigate("/galeria")}
                                className="text-base font-semibold text-black transition-colors hover:text-foodguard-500"
                            >
                                Galeria de chats
                            </button>
                        )}
                    </nav>
                </div>

                {isAuthenticated ? (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <button
                                type="button"
                                className="flex items-center justify-center bg-red-500/20 rounded-full p-4 max-w-14 max-h-14 shadow-sm shadow-black/15 cursor-pointer"
                                aria-label="Perfil de usuário"
                            >
                                <FiUser className="text-4xl text-red-500 font-extrabold" />
                            </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" className="bg-white border border-zinc-500 font-medium">
                            <DropdownMenuGroup>
                                <DropdownMenuItem
                                    onSelect={() => setProfileOpen(true)}
                                    className="outline-none hover:bg-foodguard-300/50 active:bg-foodguard-300"
                                >
                                    Editar
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                    onSelect={handleLogout}
                                    className="text-red-700 outline-none hover:bg-red-300 active:bg-red-400"
                                >
                                    Sair
                                </DropdownMenuItem>
                            </DropdownMenuGroup>
                        </DropdownMenuContent>
                    </DropdownMenu>
                ) : (
                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={() => navigate("/login")}
                            className="rounded-full border border-zinc-500 bg-white px-5 py-3 text-base font-semibold text-black shadow-sm shadow-black/15 transition-colors hover:bg-slate-100"
                        >
                            Entrar
                        </button>
                        <button
                            type="button"
                            onClick={() => navigate("/cadastro")}
                            className="rounded-full bg-foodguard-500 px-5 py-3 text-base font-semibold text-white shadow-sm shadow-black/15 transition-colors hover:bg-foodguard-500/90"
                        >
                            Cadastrar
                        </button>
                    </div>
                )}
            </div>

            {isAuthenticated && (
                <EditProfileModal open={profileOpen} onClose={() => setProfileOpen(false)} />
            )}
        </header>
    );
};

export default NavBar;
