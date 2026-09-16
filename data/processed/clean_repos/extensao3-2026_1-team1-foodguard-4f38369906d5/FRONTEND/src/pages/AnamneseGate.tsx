import { useState } from "react";
import { Navigate } from "react-router-dom";
import AuthLayout from "@/components/authLayout/AuthLayout";
import AnamneseStep from "@/components/cadastro/Anamnese";
import TransicaoStep from "@/components/cadastro/Transicao";
import { anamneseService } from "@/services/anamnese.service";
import { useAuth } from "@/hooks/use-auth";
import { extractError } from "@/lib/anamnese.constants";
import type { AnamneseRequest } from "@/models/anamnese.model";

const AnamneseGate = () => {
    const { hasAnamnese, markAnamneseDone } = useAuth();
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [done, setDone] = useState(false);

    // RN001: quem já completou a anamnese vai direto ao chat
    if (hasAnamnese && !done) return <Navigate to="/chat" replace />;

    const handleSubmit = async (data: AnamneseRequest) => {
        setSubmitting(true);
        setError(null);
        try {
            await anamneseService.criar(data);
            markAnamneseDone();
            setDone(true);
        } catch (err) {
            setError(extractError(err, "Não foi possível salvar a anamnese. Tente novamente."));
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <AuthLayout wide>
            {done ? (
                <TransicaoStep />
            ) : (
                <AnamneseStep onSubmit={handleSubmit} submitting={submitting} error={error} />
            )}
        </AuthLayout>
    );
};

export default AnamneseGate;
