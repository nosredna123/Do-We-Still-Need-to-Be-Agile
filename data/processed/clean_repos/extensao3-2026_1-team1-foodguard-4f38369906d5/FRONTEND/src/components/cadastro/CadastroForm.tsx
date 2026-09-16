import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Calendar, Mail, User } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import PasswordField from "@/components/ui/PasswordField";
import { PASSWORD_REGEX, inputClass, extractError } from "@/lib/anamnese.constants";

const NAME_REGEX = /^[a-zA-ZÀ-ÿ '-]+$/;

/** Marcador visual de campo obrigatório (C-02). */
const Required = () => (
    <span className="text-red-600" aria-hidden="true"> *</span>
);

const CadastroForm = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const { toast } = useToast();

    const [name, setName] = useState("");
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [dob, setDob] = useState("");
    const [password, setPassword] = useState("");
    const [confirm, setConfirm] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    // Limites da data de nascimento: não pode ser futura nem implausivelmente
    // antiga (C-01). Comparação lexical é segura para o formato "YYYY-MM-DD".
    const today = new Date().toISOString().slice(0, 10);
    const minDob = (() => {
        const d = new Date();
        d.setFullYear(d.getFullYear() - 120);
        return d.toISOString().slice(0, 10);
    })();

    const validate = (): string | null => {
        if (!NAME_REGEX.test(name.trim()))
            return "O nome deve conter apenas letras, espaços, apóstrofos e hífens.";
        if (name.length > 250) return "O nome deve ter no máximo 250 caracteres.";
        if (dob) {
            if (dob > today) return "A data de nascimento não pode ser uma data futura.";
            if (dob < minDob) return "Informe uma data de nascimento válida.";
        }
        if (!PASSWORD_REGEX.test(password))
            return "A senha precisa de no mínimo 8 caracteres, com maiúscula, minúscula e número.";
        if (password !== confirm) return "As senhas não coincidem.";
        return null;
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);

        const validationError = validate();
        if (validationError) {
            setError(validationError);
            toast({ variant: "error", description: validationError });
            return;
        }

        setSubmitting(true);
        try {
            await register({
                name: name.trim(),
                username: username.trim(),
                email: email.trim(),
                date_of_birth: dob || null,
                password,
                password_confirm: confirm,
            });
            toast({ variant: "success", description: "Conta criada com sucesso!" });
            navigate("/anamnese", { replace: true });
        } catch (err) {
            setError(extractError(err, "Não foi possível concluir o cadastro. Tente novamente."));
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <>
            <h2 className="font-sansita text-3xl font-extrabold tracking-tight text-black">
                CADASTRAR
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                    <div className="rounded-md bg-red-100 px-4 py-2 text-sm font-medium text-red-700">
                        {error}
                    </div>
                )}

                <p className="text-xs text-gray-700">
                    Campos marcados com <span className="text-red-600">*</span> são obrigatórios.
                </p>

                <div className="grid gap-6 sm:grid-cols-2">
                    <div className="space-y-2">
                        <label htmlFor="cadastro-nome" className="block text-sm font-semibold text-black">Nome completo<Required /></label>
                        <div className="relative">
                            <input
                                id="cadastro-nome"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                aria-required="true"
                                maxLength={250}
                                placeholder="Nome completo"
                                className={inputClass}
                            />
                            <User className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label htmlFor="cadastro-usuario" className="block text-sm font-semibold text-black">Seu usuário<Required /></label>
                        <div className="relative">
                            <input
                                id="cadastro-usuario"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                aria-required="true"
                                placeholder="Usuário"
                                className={inputClass}
                            />
                            <User className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label htmlFor="cadastro-email" className="block text-sm font-semibold text-black">Seu email<Required /></label>
                        <div className="relative">
                            <input
                                id="cadastro-email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                aria-required="true"
                                placeholder="Email"
                                className={inputClass}
                            />
                            <Mail className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label htmlFor="cadastro-dob" className="block text-sm font-semibold text-black">
                            Data de nascimento{" "}
                            <span className="font-normal text-gray-700">(opcional)</span>
                        </label>
                        <div className="relative">
                            <input
                                id="cadastro-dob"
                                type="date"
                                value={dob}
                                onChange={(e) => setDob(e.target.value)}
                                min={minDob}
                                max={today}
                                className={inputClass}
                            />
                            <Calendar className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-800" />
                        </div>
                    </div>

                    <PasswordField
                        id="cadastro-senha"
                        label={<>Sua senha<Required /></>}
                        value={password}
                        onChange={setPassword}
                        required
                        autoComplete="new-password"
                        placeholder="Senha"
                        inputClassName={inputClass}
                        showStrength
                    />

                    <PasswordField
                        id="cadastro-confirmar-senha"
                        label={<>Confirmar a senha<Required /></>}
                        value={confirm}
                        onChange={setConfirm}
                        required
                        autoComplete="new-password"
                        placeholder="Confirme a senha"
                        inputClassName={inputClass}
                        error={
                            confirm.length > 0 && confirm !== password
                                ? "As senhas não coincidem."
                                : undefined
                        }
                    />
                </div>

                <div>
                    <button
                        type="submit"
                        disabled={submitting}
                        className="h-12 w-full rounded-lg bg-foodguard-500 font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-500/90 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {submitting ? "Cadastrando..." : "Continuar"}
                    </button>

                    <p className="text-sm text-black mt-3">
                        Já possui conta?{" "}
                        <Link to="/login" className="font-bold uppercase text-foodguard-500 hover:underline">
                            Acessar
                        </Link>
                    </p>
                </div>
            </form>
        </>
    );
};

export default CadastroForm;
