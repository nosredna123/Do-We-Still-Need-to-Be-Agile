import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";
import { Eye, EyeOff, Mail } from "lucide-react";
import AuthLayout from "@/components/authLayout/AuthLayout";
import { useAuth } from "@/hooks/use-auth";

const Login = () => {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        setSubmitting(true);
        try {
            await login({ email: email.trim(), password });
            // RN001: o gate de anamnese decide entre /galeria e /anamnese
            navigate("/galeria", { replace: true });
        } catch (err) {
            // Mensagem genérica por privacidade (RF003)
            if (err instanceof AxiosError && err.response?.status === 401) {
                setError("Email ou senha incorretos.");
            } else {
                setError("Não foi possível entrar. Tente novamente.");
            }
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <AuthLayout>
            <h2 className="font-sansita text-3xl font-bold text-black">
                ACESSAR
            </h2>

            <form onSubmit={handleSubmit} className="space-y-12">
                {error && (
                    <div className="rounded-md bg-red-100 px-4 py-2 text-sm font-medium text-red-700">
                        {error}
                    </div>
                )}

                <div className="space-y-2">
                    <label htmlFor="email" className="block font-semibold text-black">
                        Seu email
                    </label>
                    <div className="relative">
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="Email"
                            className="h-12 w-full rounded-md border border-zinc-500 bg-slate-50 px-4 pr-10 text-black placeholder:text-gray-700 focus:border-foodguard-500 focus:outline-none focus:ring-2 focus:ring-foodguard-500/30"
                        />
                        <Mail className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
                    </div>
                </div>

                <div className="space-y-2">
                    <label htmlFor="password" className="block font-semibold text-black">
                        Sua senha
                    </label>
                    <div className="relative">
                        <input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Senha"
                            className="h-12 w-full rounded-md border border-zinc-500 bg-slate-50 px-4 pr-10 text-black placeholder:text-gray-700 focus:border-foodguard-500 focus:outline-none focus:ring-2 focus:ring-foodguard-500/30"
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword((s) => !s)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-800 hover:text-black"
                            aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                        >
                            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                        </button>
                    </div>
                </div>

                <div>
                    <button
                        type="submit"
                        disabled={submitting}
                        className="h-12 w-full rounded-lg bg-foodguard-500 font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-500/90 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {submitting ? "Entrando..." : "Entrar"}
                    </button>

                    <p className="text-sm text-black mt-3">
                        Não possui conta?{" "}
                        <Link to="/cadastro" className="font-bold uppercase text-foodguard-500 hover:underline">
                            Cadastrar-se
                        </Link>
                    </p>
                </div>

            </form>
        </AuthLayout>
    );
};

export default Login;
