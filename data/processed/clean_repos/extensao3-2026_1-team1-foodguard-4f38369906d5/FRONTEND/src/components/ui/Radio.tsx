type RadioProps = {
    name: string;
    value: string;
    checked: boolean;
    onChange: (v: string) => void;
    label: string;
    /** Quando true, desabilita o input e remove o cursor de ponteiro. */
    disabled?: boolean;
};

/**
 * Radio button estilizado e compartilhado (cadastro/Anamnese e perfil).
 */
const Radio = ({ name, value, checked, onChange, label, disabled = false }: RadioProps) => (
    <label
        className={`flex items-center gap-2 text-black ${disabled ? "cursor-not-allowed" : "cursor-pointer"
            }`}
    >
        <input
            type="radio"
            name={name}
            value={value}
            checked={checked}
            onChange={() => onChange(value)}
            disabled={disabled}
            className="peer sr-only"
        />
        <span
            className={`flex h-5 w-5 items-center justify-center rounded-full border-2 transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-foodguard-500 peer-focus-visible:ring-offset-2 ${checked ? "border-foodguard-700" : "border-zinc-500"
                }`}
        >
            {checked && <span className="h-2.5 w-2.5 rounded-full bg-foodguard-500" />}
        </span>
        <span className="text-sm">{label}</span>
    </label>
);

export default Radio;
