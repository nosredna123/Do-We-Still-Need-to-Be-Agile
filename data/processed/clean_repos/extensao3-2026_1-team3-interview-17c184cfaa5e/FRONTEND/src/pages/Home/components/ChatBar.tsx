import { Box, Chip, Paper } from "@mui/material";

type ScenarioType = "interview" | "improve";

type ChatBarProps = {
    onSelectScenario: (scenario: ScenarioType) => void;
    disabled?: boolean;
    visible?: boolean;
    nivelCompatibilidade?: number;
    loadingScenario?: ScenarioType | null;
    selectedScenarios?: ScenarioType[];
};

function ChatBar({
    onSelectScenario,
    disabled = false,
    visible = true,
    nivelCompatibilidade,
    loadingScenario = null,
    selectedScenarios = [],
}: ChatBarProps) {
    if (!visible) return null;

    const compatibilidadeMinimaParaEntrevista = 50;

    const podeSimularEntrevista =
        nivelCompatibilidade === undefined ||
        nivelCompatibilidade >= compatibilidadeMinimaParaEntrevista;

    const podeMelhorar =
        nivelCompatibilidade === undefined ||
        nivelCompatibilidade < 100;

    const isScenarioDisabled = (scenario: ScenarioType) =>
        disabled ||
        loadingScenario === scenario ||
        selectedScenarios.includes(scenario);

    const getScenarioLabel = (
        scenario: ScenarioType,
        defaultLabel: string
    ) => {
        if (loadingScenario === scenario) {
            return "Carregando...";
        }

        if (selectedScenarios.includes(scenario)) {
            return `${defaultLabel} gerado`;
        }

        return defaultLabel;
    };

    return (
        <Paper
            elevation={0}
            sx={{
                p: 2,
                mt: 3,
                borderRadius: 4,
                backgroundColor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    gap: 1.5,
                    flexWrap: "wrap",
                }}
            >
                {podeSimularEntrevista && (
                    <Chip
                        label={getScenarioLabel(
                            "interview",
                            "Simular perguntas"
                        )}
                        clickable
                        disabled={isScenarioDisabled("interview")}
                        onClick={() => onSelectScenario("interview")}
                    />
                )}

                {podeMelhorar && (
                    <Chip
                        label={getScenarioLabel(
                            "improve",
                            "Como melhorar"
                        )}
                        clickable
                        disabled={isScenarioDisabled("improve")}
                        onClick={() => onSelectScenario("improve")}
                    />
                )}
            </Box>
        </Paper>
    );
}

export default ChatBar;
export type { ScenarioType };