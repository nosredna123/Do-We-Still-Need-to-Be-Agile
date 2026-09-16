import { useId, useState, type ReactNode } from "react";
import { Eye, EyeOff, Check, X } from "lucide-react";
import { cn } from "@/lib/utils";
import {
    PASSWORD_CRITERIA,
    evaluatePassword,
    type PasswordStrength,
} from "@/lib/password";

type PasswordFieldProps = {
    id?: string;
    label: ReactNode;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    required?: boolean;
    disabled?: boolean;
    autoComplete?: string;
    /** Classe do input — mantém o estilo do formulário hospedeiro. */
    inputClassName: string;
    /** Exibe o checklist de requisitos e a barra de força (campo de nova senha). */
    showStrength?: boolean;
    /** Mensagem de erro inline (ex.: confirmação que não coincide). */
    error?: string;
};

const STRENGTH_META: Record<
    PasswordStrength,
    { label: string; bar: string; text: string; filled: number }
> = {
    weak: { label: "Fraca", bar: "bg-red-500", text: "text-red-600", filled: 1 },
    medium: { label: "Média", bar: "bg-yellow-500", text: "text-yellow-600", filled: 2 },
    strong: { label: "Forte", bar: "bg-foodguard-500", text: "text-foodguard-600", filled: 3 },
};

/**
 * Campo de senha reutilizável: alterna mostrar/ocultar e, opcionalmente,
 * exibe feedback de força + checklist de requisitos em tempo real (A-03).
 */
const PasswordField = ({
    id,
    label,
    value,
    onChange,
    placeholder,
    required = false,
    disabled = false,
    autoComplete,
    inputClassName,
    showStrength = false,
    error,
}: PasswordFieldProps) => {
    const generatedId = useId();
    const fieldId = id ?? generatedId;
    const errorId = `${fieldId}-error`;
    const [visible, setVisible] = useState(false);

    const result = evaluatePassword(value);
    const meta = STRENGTH_META[result.strength];
    const showFeedback = showStrength && value.length > 0;

    return (
        <div className="space-y-2">
            <label htmlFor={fieldId} className="block text-sm font-semibold text-black">
                {label}
            </label>

            <div className="relative">
                <input
                    id={fieldId}
                    type={visible ? "text" : "password"}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    required={required}
                    aria-required={required || undefined}
                    aria-invalid={error ? true : undefined}
                    aria-describedby={error ? errorId : undefined}
                    disabled={disabled}
                    placeholder={placeholder}
                    autoComplete={autoComplete}
                    className={inputClassName}
                />
                <button
                    type="button"
                    onClick={() => setVisible((v) => !v)}
                    disabled={disabled}
                    aria-label={visible ? "Ocultar senha" : "Mostrar senha"}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-800 hover:text-black disabled:opacity-50"
                >
                    {visible ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
            </div>

            {showFeedback && (
                <div className="space-y-2">
                    <div className="flex items-center gap-2">
                        <div className="flex flex-1 gap-1">
                            {[0, 1, 2].map((i) => (
                                <span
                                    key={i}
                                    className={cn(
                                        "h-1.5 flex-1 rounded-full transition-colors",
                                        i < meta.filled ? meta.bar : "bg-gray-200",
                                    )}
                                />
                            ))}
                        </div>
                        <span className={cn("text-xs font-semibold", meta.text)}>
                            {meta.label}
                        </span>
                    </div>

                    <ul className="space-y-1">
                        {PASSWORD_CRITERIA.map((criterion) => {
                            const ok = result.passed[criterion.id];
                            return (
                                <li
                                    key={criterion.id}
                                    className="flex items-center gap-1.5 text-xs"
                                >
                                    {ok ? (
                                        <Check className="h-3.5 w-3.5 shrink-0 text-foodguard-600" />
                                    ) : (
                                        <X className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                                    )}
                                    <span className={ok ? "text-foodguard-700" : "text-gray-600"}>
                                        {criterion.label}
                                    </span>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}

            {error && (
                <p id={errorId} className="text-xs font-medium text-red-600">
                    {error}
                </p>
            )}
        </div>
    );
};

export default PasswordField;
