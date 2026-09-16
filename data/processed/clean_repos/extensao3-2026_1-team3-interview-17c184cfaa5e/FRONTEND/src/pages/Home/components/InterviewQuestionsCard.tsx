import { Box, Paper, Typography, Divider, useTheme } from "@mui/material";

type Props = {
    title?: string;
    questions: string[];
};

export default function InterviewQuestionsCard({
    title = "Perguntas simuladas da entrevista",
    questions,
}: Props) {
    const theme = useTheme();
    const isDark = theme.palette.mode === "dark";

    const colors = {
        paperBg: isDark
            ? "linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(15,23,42,0.92) 100%)"
            : "linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",

        paperBorder: isDark
            ? "1px solid rgba(148, 163, 184, 0.25)"
            : "1px solid rgba(148, 163, 184, 0.30)",

        titleColor: isDark ? "#d1fae5" : "#14532d",
        textPrimary: isDark ? "#f8fafc" : "#0f172a",
        textSecondary: isDark ? "#cbd5e1" : "#475569",
        textMuted: isDark ? "#94a3b8" : "#64748b",

        cardBg: isDark
            ? "rgba(255, 255, 255, 0.045)"
            : "rgba(248, 250, 252, 0.95)",

        cardBorder: isDark
            ? "1px solid rgba(255, 255, 255, 0.09)"
            : "1px solid rgba(148, 163, 184, 0.25)",

        badgeBg: isDark
            ? "rgba(59, 130, 246, 0.14)"
            : "rgba(37, 99, 235, 0.10)",

        badgeColor: isDark ? "#bfdbfe" : "#1d4ed8",

        divider: isDark
            ? "rgba(255,255,255,0.10)"
            : "rgba(148, 163, 184, 0.28)",
    };

    return (
        <Paper
            elevation={0}
            sx={{
                mt: 3,
                p: { xs: 3, md: 4 },
                borderRadius: "32px",
                background: colors.paperBg,
                border: colors.paperBorder,
                color: colors.textPrimary,
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 2,
                    mb: 2,
                    flexWrap: "wrap",
                }}
            >
                <Box>
                    <Typography
                        variant="h6"
                        sx={{
                            fontWeight: 800,
                            color: colors.titleColor,
                            mb: 0.5,
                        }}
                    >
                        {title}
                    </Typography>

                    <Typography
                        variant="body2"
                        sx={{
                            color: colors.textMuted,
                            lineHeight: 1.6,
                        }}
                    >
                        Use estas perguntas para praticar respostas antes da entrevista.
                    </Typography>
                </Box>

                <Box
                    sx={{
                        px: 1.8,
                        py: 0.8,
                        borderRadius: "999px",
                        backgroundColor: colors.badgeBg,
                        color: colors.badgeColor,
                        fontWeight: 800,
                        fontSize: "0.85rem",
                    }}
                >
                    {questions.length} perguntas
                </Box>
            </Box>

            <Divider sx={{ borderColor: colors.divider, mb: 3 }} />

            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                    gap: 2,
                }}
            >
                {questions.map((question, index) => (
                    <Box
                        key={`${question}-${index}`}
                        sx={{
                            p: 2.5,
                            borderRadius: "22px",
                            backgroundColor: colors.cardBg,
                            border: colors.cardBorder,
                            display: "flex",
                            gap: 1.5,
                            alignItems: "flex-start",
                        }}
                    >
                        <Box
                            sx={{
                                width: 32,
                                height: 32,
                                minWidth: 32,
                                borderRadius: "50%",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                backgroundColor: colors.badgeBg,
                                color: colors.badgeColor,
                                fontWeight: 900,
                                fontSize: "0.9rem",
                            }}
                        >
                            {index + 1}
                        </Box>

                        <Box>
                            <Typography
                                variant="subtitle2"
                                sx={{
                                    fontWeight: 800,
                                    color: colors.textPrimary,
                                    mb: 0.6,
                                }}
                            >
                                Pergunta {index + 1}
                            </Typography>

                            <Typography
                                variant="body2"
                                sx={{
                                    color: colors.textSecondary,
                                    lineHeight: 1.7,
                                }}
                            >
                                {question}
                            </Typography>
                        </Box>
                    </Box>
                ))}
            </Box>
        </Paper>
    );
}