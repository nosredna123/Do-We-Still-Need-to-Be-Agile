import { useRef, useState } from "react";
import { Box, Button, Container, Paper, Fade, Slide } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import UploadCard from "./components/UploadCard";
import JobCard from "./components/JobCard";
import ResultCard from "./components/ResultCard";
import ChatBar from "./components/ChatBar";
import type { ScenarioType } from "./components/ChatBar";
import ThemeToggleButton from "../../components/ThemeToggleButton";
import {
    analyzeResume,
    getInterviewQuestions,
    getImprovementRecommendations,
} from "../../services/analyzerService";
import type { AnalyzeResumeResponse } from "../../models/analyzer";
import { useLoading } from "../../contexts/LoadingContext";
import { ImproveResultCard } from "./components/ImproveResultCard";
import type { ImproveResponse } from "../../models/improve";
import { JobDescriptionDialog } from "./components/JobDescriptionDialog";
import InterviewQuestionsCard from "./components/InterviewQuestionsCard";

function HomePage() {
    const [resumePdf, setResumePdf] = useState<File | null>(null);
    const [jobDescription, setJobDescription] = useState("");
    const [jobDescriptionDialogOpen, setJobDescriptionDialogOpen] = useState(false);
    const [resultado, setResultado] = useState<AnalyzeResumeResponse | null>(null);
    const [erro, setErro] = useState("");
    const [mostrarCards, setMostrarCards] = useState(true);
    const [mostrarResultado, setMostrarResultado] = useState(false);

    const [respostaExtraTitulo, setRespostaExtraTitulo] = useState("");
    const [respostaExtraItems, setRespostaExtraItems] = useState<string[]>([]);

    const [improveResponse, setImproveResponse] = useState<ImproveResponse | null>(null);

    const [loadingScenario, setLoadingScenario] = useState<ScenarioType | null>(null);
    const [selectedScenarios, setSelectedScenarios] = useState<ScenarioType[]>([]);

    const respostaExtraRef = useRef<HTMLDivElement | null>(null);

    const { openLoading, closeLoading, isLoading } = useLoading();

    const handleAnalisar = async (jobDescriptionValue = jobDescription) => {
        const descricaoVaga = jobDescriptionValue.trim();

        if (!resumePdf || !descricaoVaga) {
            setErro("Por favor, envie o currículo em PDF e informe o texto da vaga.");
            return;
        }

        setErro("");
        setResultado(null);
        setMostrarResultado(false);
        setMostrarCards(true);
        setRespostaExtraTitulo("");
        setRespostaExtraItems([]);
        setImproveResponse(null);
        setLoadingScenario(null);
        setSelectedScenarios([]);

        openLoading("Analisando vaga...");

        try {
            const response = await analyzeResume({
                job_description: descricaoVaga,
                resume_pdf: resumePdf,
            });

            setMostrarCards(false);

            setTimeout(() => {
                setResultado(response);
                setMostrarResultado(true);
            }, 450);
        } catch (error: any) {
            console.error("ERRO COMPLETO NO HANDLE_ANALISAR:", error);
            console.error("error.response?.data:", error?.response?.data);
            console.error("error.message:", error?.message);

            setErro(
                error?.response?.data?.detail ||
                    error?.response?.data?.mensagem ||
                    error?.message ||
                    "Erro ao conectar com o servidor."
            );
        } finally {
            closeLoading();
        }
    };

    const montarResumeTextParaImprove = (resultado: AnalyzeResumeResponse) => {
        return `
Título da vaga: ${resultado.titulo_vaga}

Resumo da análise:
${resultado.resumo}

Nível de compatibilidade:
${resultado.nivel_compatibilidade}%

Pontos fortes:
${resultado.pontos_fortes.join("\n")}

Pontos fracos:
${resultado.pontos_fracos.join("\n")}

Habilidades da vaga:
${resultado.habilidades_vaga.join("\n")}

Habilidades faltantes:
${resultado.habilidades_faltantes.join("\n")}

Recomendação:
${resultado.recomendacao}
`.trim();
    };

    const handleSelectScenario = async (scenario: ScenarioType) => {
        if (!resultado) return;

        if (loadingScenario) return;

        if (selectedScenarios.includes(scenario)) return;

        setErro("");
        setLoadingScenario(scenario);

        try {
            if (scenario === "interview") {
                openLoading("Gerando perguntas da entrevista...");

                const response = await getInterviewQuestions(resultado);

                setRespostaExtraTitulo("Perguntas simuladas da entrevista");
                setRespostaExtraItems(
                    response?.perguntas ||
                        response?.questions ||
                        []
                );
            }

            if (scenario === "improve") {
                openLoading("Gerando recomendações de melhoria...");

                const response = await getImprovementRecommendations({
                    resume_text: montarResumeTextParaImprove(resultado),
                    titulo_vaga: resultado.titulo_vaga,
                    habilidades_vaga: resultado.habilidades_vaga,
                    nivel_compatibilidade: resultado.nivel_compatibilidade,
                    pontos_fortes: resultado.pontos_fortes,
                    pontos_fracos: resultado.pontos_fracos,
                    habilidades_faltantes: resultado.habilidades_faltantes,
                    recomendacao: resultado.recomendacao,
                    resumo: resultado.resumo,
                });

                setImproveResponse(response);
            }

            setSelectedScenarios((prev) => {
                if (prev.includes(scenario)) {
                    return prev;
                }

                return [...prev, scenario];
            });

            setTimeout(() => {
                respostaExtraRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }, 100);
        } catch (error: any) {
            setErro(
                error?.response?.data?.detail ||
                    error?.response?.data?.mensagem ||
                    "Erro ao buscar conteúdo complementar."
            );
        } finally {
            setLoadingScenario(null);
            closeLoading();
        }
    };

    const handleConfirmJobDescription = (texto: string) => {
        setJobDescription(texto);
        setJobDescriptionDialogOpen(false);
        handleAnalisar(texto);
    };

    const handleVoltarInicio = () => {
        setMostrarResultado(false);
        setMostrarCards(true);
        setResultado(null);
        setRespostaExtraTitulo("");
        setRespostaExtraItems([]);
        setImproveResponse(null);
        setLoadingScenario(null);
        setSelectedScenarios([]);
        setErro("");
    };

    return (
        <Box sx={{ minHeight: "100vh", backgroundColor: "background.default", py: 6 }}>
            <Container
                maxWidth={false}
                sx={{
                    width: "100%",
                    maxWidth: "1180px",
                    mx: "auto",
                }}
            >
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "flex-end",
                        mb: 2,
                    }}
                >
                    <ThemeToggleButton />
                </Box>

                <Box
                    sx={{
                        mb: 4,
                        minHeight: { xs: 520, md: 360 },
                    }}
                >
                    {mostrarCards && (
                        <Box
                            sx={{
                                display: "grid",
                                gridTemplateColumns: {
                                    xs: "1fr",
                                    md: "1fr 1fr",
                                },
                                gap: 4,
                                alignItems: "stretch",
                            }}
                        >
                            <Slide
                                direction="left"
                                in={mostrarCards}
                                timeout={450}
                                mountOnEnter
                                unmountOnExit
                            >
                                <Box>
                                    <UploadCard
                                        arquivo={resumePdf}
                                        onFileChange={setResumePdf}
                                    />
                                </Box>
                            </Slide>

                            <Slide
                                direction="right"
                                in={mostrarCards}
                                timeout={450}
                                mountOnEnter
                                unmountOnExit
                            >
                                <Box>
                                    <JobCard
                                        jobDescription={jobDescription}
                                        onOpenJobDescription={() =>
                                            setJobDescriptionDialogOpen(true)
                                        }
                                        loading={isLoading}
                                    />
                                </Box>
                            </Slide>
                        </Box>
                    )}

                    <Fade
                        in={mostrarResultado}
                        timeout={550}
                        mountOnEnter
                        unmountOnExit
                    >
                        <Box
                            sx={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 1,
                            }}
                        >
                            <Box
                                sx={{
                                    display: "flex",
                                    justifyContent: "flex-start",
                                    mb: 1,
                                }}
                            >
                                <Button
                                    variant="outlined"
                                    startIcon={<ArrowBackIcon />}
                                    onClick={handleVoltarInicio}
                                    sx={{
                                        borderRadius: 999,
                                        textTransform: "none",
                                        fontWeight: 700,
                                        px: 2.5,
                                    }}
                                >
                                    Voltar
                                </Button>
                            </Box>

                            {resultado && <ResultCard resultado={resultado} />}

                            <Box ref={respostaExtraRef}>
                                {respostaExtraItems.length > 0 && (
                                    <InterviewQuestionsCard
                                        title={respostaExtraTitulo}
                                        questions={respostaExtraItems}
                                    />
                                )}

                                {improveResponse && (
                                    <ImproveResultCard data={improveResponse} />
                                )}
                            </Box>

                            <ChatBar
                                visible={!!resultado}
                                nivelCompatibilidade={resultado?.nivel_compatibilidade}
                                onSelectScenario={handleSelectScenario}
                                loadingScenario={loadingScenario}
                                selectedScenarios={selectedScenarios}
                            />
                        </Box>
                    </Fade>
                </Box>

                {erro && (
                    <Paper
                        elevation={0}
                        sx={{
                            p: 2,
                            mb: 3,
                            borderRadius: 3,
                            backgroundColor: "#fff4f4",
                            color: "#b42318",
                            border: "1px solid #fecaca",
                        }}
                    >
                        {erro}
                    </Paper>
                )}

                <JobDescriptionDialog
                    open={jobDescriptionDialogOpen}
                    initialValue={jobDescription}
                    loading={isLoading}
                    onClose={() => setJobDescriptionDialogOpen(false)}
                    onConfirm={handleConfirmJobDescription}
                />
            </Container>
        </Box>
    );
}

export default HomePage;