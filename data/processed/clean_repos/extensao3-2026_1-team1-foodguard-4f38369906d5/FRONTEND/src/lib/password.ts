/**
 * Critérios e força de senha para feedback visual em tempo real.
 *
 * Os critérios espelham o `PASSWORD_REGEX` de `anamnese.constants.ts`
 * (mín. 8 caracteres, com maiúscula, minúscula e número): a senha é válida
 * quando todos os critérios passam.
 */
export type PasswordCriterion = {
    id: string;
    label: string;
    test: (password: string) => boolean;
};

export const PASSWORD_CRITERIA: PasswordCriterion[] = [
    { id: "length", label: "No mínimo 8 caracteres", test: (p) => p.length >= 8 },
    { id: "uppercase", label: "Uma letra maiúscula", test: (p) => /[A-Z]/.test(p) },
    { id: "lowercase", label: "Uma letra minúscula", test: (p) => /[a-z]/.test(p) },
    { id: "number", label: "Um número", test: (p) => /\d/.test(p) },
];

export type PasswordStrength = "weak" | "medium" | "strong";

export interface PasswordEvaluation {
    /** Mapa id-do-critério → cumprido. */
    passed: Record<string, boolean>;
    /** Quantidade de critérios cumpridos. */
    metCount: number;
    /** True quando todos os critérios obrigatórios são cumpridos. */
    isValid: boolean;
    strength: PasswordStrength;
}

/** Avalia uma senha, retornando critérios cumpridos e nível de força. */
export const evaluatePassword = (password: string): PasswordEvaluation => {
    const passed: Record<string, boolean> = {};
    let metCount = 0;
    for (const criterion of PASSWORD_CRITERIA) {
        const ok = criterion.test(password);
        passed[criterion.id] = ok;
        if (ok) metCount += 1;
    }

    const isValid = metCount === PASSWORD_CRITERIA.length;
    // Bônus que diferencia "forte": comprimento generoso ou símbolo.
    const hasBonus = password.length >= 12 || /[^A-Za-z0-9]/.test(password);

    let strength: PasswordStrength = "weak";
    if (isValid && hasBonus) strength = "strong";
    else if (metCount >= 3) strength = "medium";

    return { passed, metCount, isValid, strength };
};
