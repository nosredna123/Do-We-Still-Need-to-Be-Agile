import type { ReactNode } from "react";
import {
    Box,
    Chip,
    Divider,
    LinearProgress,
    Paper,
    Typography,
    useTheme,
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import type { AnalyzeResumeResponse } from "../../../models/analyzer";

type Props = {
    resultado: AnalyzeResumeResponse;
};

function getCompatibilityLabel(value: number) {
    if (value >= 80) return "Boa compatibilidade";
    if (value >= 60) return "Compatibilidade moderada";
    return "Baixa compatibilidade";
}

function getRecommendationColor(recomendacao: string, isDark: boolean) {
    const value = recomendacao.toLowerCase();

    if (value.includes("recomendado") || value.includes("aprovado")) {
        return {
            color: isDark ? "#bbf7d0" : "#166534",
            backgroundColor: isDark
                ? "rgba(34, 197, 94, 0.14)"
                : "rgba(22, 101, 52, 0.08)",
            border: isDark
                ? "1px solid rgba(34, 197, 94, 0.35)"
                : "1px solid rgba(22, 101, 52, 0.22)",
        };
    }

    if (value.includes("desenvolvimento") || value.includes("atenção")) {
        return {
            color: isDark ? "#fde68a" : "#92400e",
            backgroundColor: isDark
                ? "rgba(245, 158, 11, 0.14)"
                : "rgba(245, 158, 11, 0.10)",
            border: isDark
                ? "1px solid rgba(245, 158, 11, 0.35)"
                : "1px solid rgba(146, 64, 14, 0.22)",
        };
    }

    return {
        color: isDark ? "#bfdbfe" : "#1d4ed8",
        backgroundColor: isDark
            ? "rgba(59, 130, 246, 0.14)"
            : "rgba(59, 130, 246, 0.08)",
        border: isDark
            ? "1px solid rgba(59, 130, 246, 0.35)"
            : "1px solid rgba(29, 78, 216, 0.20)",
    };
}

function CircleIcon({
    children,
    color,
    backgroundColor,
}: {
    children: ReactNode;
    color: string;
    backgroundColor: string;
}) {
    return (
        <Box
            component="span"
            sx={{
                width: 28,
                height: 28,
                borderRadius: "50%",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                color,
                backgroundColor,
                fontWeight: 900,
                fontSize: "0.95rem",
                flexShrink: 0,
            }}
        >
            {children}
        </Box>
    );
}

function SectionList({
    title,
    items,
    icon,
    colors,
}: {
    title: string;
    items: string[];
    icon: ReactNode;
    colors: {
        sectionBg: string;
        sectionBorder: string;
        textPrimary: string;
        textSecondary: string;
    };
}) {
    return (
        <Box
            sx={{
                p: 2.5,
                borderRadius: "22px",
                backgroundColor: colors.sectionBg,
                border: colors.sectionBorder,
                height: "100%",
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    mb: 1.5,
                }}
            >
                {icon}

                <Typography
                    variant="subtitle2"
                    sx={{
                        fontWeight: 800,
                        color: colors.textPrimary,
                    }}
                >
                    {title}
                </Typography>
            </Box>

            <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                {items.map((item, index) => (
                    <Box component="li" key={`${title}-${index}`} sx={{ mb: 0.8 }}>
                        <Typography
                            variant="body2"
                            sx={{
                                lineHeight: 1.6,
                                color: colors.textSecondary,
                            }}
                        >
                            {item}
                        </Typography>
                    </Box>
                ))}
            </Box>
        </Box>
    );
}

export default function ResultCard({ resultado }: Props) {
    const theme = useTheme();
    const isDark = theme.palette.mode === "dark";

    const compatibility = resultado.nivel_compatibilidade;
    const recommendationStyle = getRecommendationColor(resultado.recomendacao, isDark);

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

        compatibilityBg: isDark
            ? "rgba(59, 130, 246, 0.10)"
            : "rgba(239, 246, 255, 0.95)",

        compatibilityBorder: isDark
            ? "1px solid rgba(59, 130, 246, 0.25)"
            : "1px solid rgba(59, 130, 246, 0.22)",

        compatibilityText: isDark ? "#bfdbfe" : "#1d4ed8",

        progressBg: isDark
            ? "rgba(255,255,255,0.08)"
            : "rgba(148, 163, 184, 0.22)",

        progressBar: isDark ? "#93c5fd" : "#2563eb",

        divider: isDark
            ? "rgba(255,255,255,0.10)"
            : "rgba(148, 163, 184, 0.28)",

        chipBg: isDark
            ? "rgba(148, 163, 184, 0.14)"
            : "rgba(226, 232, 240, 0.75)",

        chipBorder: isDark
            ? "1px solid rgba(148, 163, 184, 0.22)"
            : "1px solid rgba(148, 163, 184, 0.32)",

        chipText: isDark ? "#e2e8f0" : "#334155",

        successIconColor: isDark ? "#86efac" : "#15803d",
        successIconBg: isDark ? "rgba(34, 197, 94, 0.14)" : "rgba(22, 163, 74, 0.10)",

        warningIconColor: isDark ? "#facc15" : "#a16207",
        warningIconBg: isDark ? "rgba(250, 204, 21, 0.14)" : "rgba(202, 138, 4, 0.10)",

        infoIconColor: isDark ? "#93c5fd" : "#1d4ed8",
        infoIconBg: isDark ? "rgba(147, 197, 253, 0.14)" : "rgba(37, 99, 235, 0.10)",
    };

    return (
        <Paper
            elevation={0}
            sx={{
                p: { xs: 3, md: 4 },
                mb: 4,
                borderRadius: "32px",
                border: colors.paperBorder,
                background: colors.paperBg,
                color: colors.textPrimary,
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 2,
                    mb: 3,
                    flexWrap: "wrap",
                }}
            >
                <Typography
                    variant="h6"
                    sx={{
                        fontWeight: 800,
                        color: colors.titleColor,
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                    }}
                >
                    <AutoAwesomeIcon />
                    Resultado da Análise
                </Typography>

                <Chip
                    label={resultado.recomendacao}
                    sx={{
                        ...recommendationStyle,
                        fontWeight: 800,
                    }}
                />
            </Box>

            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: { xs: "1fr", md: "1.4fr 0.8fr" },
                    gap: 2.5,
                    mb: 3,
                }}
            >
                <Box
                    sx={{
                        p: 2.5,
                        borderRadius: "24px",
                        backgroundColor: colors.cardBg,
                        border: colors.cardBorder,
                    }}
                >
                    <Typography
                        variant="caption"
                        sx={{
                            color: colors.textMuted,
                            fontWeight: 800,
                            textTransform: "uppercase",
                            letterSpacing: 0.8,
                        }}
                    >
                        Título da vaga
                    </Typography>

                    <Typography
                        variant="h5"
                        sx={{
                            mt: 1,
                            fontWeight: 850,
                            color: colors.textPrimary,
                            lineHeight: 1.25,
                        }}
                    >
                        {resultado.titulo_vaga}
                    </Typography>
                </Box>

                <Box
                    sx={{
                        p: 2.5,
                        borderRadius: "24px",
                        backgroundColor: colors.compatibilityBg,
                        border: colors.compatibilityBorder,
                    }}
                >
                    <Typography
                        variant="caption"
                        sx={{
                            color: colors.textMuted,
                            fontWeight: 800,
                            textTransform: "uppercase",
                            letterSpacing: 0.8,
                        }}
                    >
                        Compatibilidade
                    </Typography>

                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "baseline",
                            gap: 1,
                            mt: 1,
                            flexWrap: "wrap",
                        }}
                    >
                        <Typography
                            variant="h3"
                            sx={{
                                fontWeight: 900,
                                color: colors.compatibilityText,
                                lineHeight: 1,
                            }}
                        >
                            {compatibility}%
                        </Typography>

                        <Typography
                            variant="body2"
                            sx={{
                                color: colors.textSecondary,
                                fontWeight: 700,
                            }}
                        >
                            {getCompatibilityLabel(compatibility)}
                        </Typography>
                    </Box>

                    <LinearProgress
                        variant="determinate"
                        value={compatibility}
                        sx={{
                            mt: 2,
                            height: 9,
                            borderRadius: 999,
                            backgroundColor: colors.progressBg,
                            "& .MuiLinearProgress-bar": {
                                borderRadius: 999,
                                backgroundColor: colors.progressBar,
                            },
                        }}
                    />
                </Box>
            </Box>

            <Box
                sx={{
                    p: 2.5,
                    borderRadius: "24px",
                    backgroundColor: colors.cardBg,
                    border: colors.cardBorder,
                    mb: 3,
                }}
            >
                <Typography
                    variant="subtitle2"
                    sx={{
                        fontWeight: 800,
                        mb: 1,
                        color: colors.textPrimary,
                    }}
                >
                    Resumo
                </Typography>

                <Typography
                    variant="body1"
                    sx={{
                        lineHeight: 1.7,
                        color: colors.textSecondary,
                    }}
                >
                    {resultado.resumo}
                </Typography>
            </Box>

            <Box sx={{ mb: 3 }}>
                <Typography
                    variant="subtitle2"
                    sx={{
                        fontWeight: 800,
                        mb: 1.5,
                        color: colors.textPrimary,
                    }}
                >
                    Habilidades da vaga
                </Typography>

                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    {resultado.habilidades_vaga.map((item) => (
                        <Chip
                            key={item}
                            label={item}
                            sx={{
                                color: colors.chipText,
                                backgroundColor: colors.chipBg,
                                border: colors.chipBorder,
                                fontWeight: 700,
                            }}
                        />
                    ))}
                </Box>
            </Box>

            <Divider sx={{ borderColor: colors.divider, mb: 3 }} />

            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
                    gap: 2,
                }}
            >
                <SectionList
                    title="Pontos fortes"
                    items={resultado.pontos_fortes}
                    colors={{
                        sectionBg: colors.cardBg,
                        sectionBorder: colors.cardBorder,
                        textPrimary: colors.textPrimary,
                        textSecondary: colors.textSecondary,
                    }}
                    icon={
                        <CircleIcon
                            color={colors.successIconColor}
                            backgroundColor={colors.successIconBg}
                        >
                            ✓
                        </CircleIcon>
                    }
                />

                <SectionList
                    title="Pontos fracos"
                    items={resultado.pontos_fracos}
                    colors={{
                        sectionBg: colors.cardBg,
                        sectionBorder: colors.cardBorder,
                        textPrimary: colors.textPrimary,
                        textSecondary: colors.textSecondary,
                    }}
                    icon={
                        <CircleIcon
                            color={colors.warningIconColor}
                            backgroundColor={colors.warningIconBg}
                        >
                            !
                        </CircleIcon>
                    }
                />

                <SectionList
                    title="Habilidades faltantes"
                    items={resultado.habilidades_faltantes}
                    colors={{
                        sectionBg: colors.cardBg,
                        sectionBorder: colors.cardBorder,
                        textPrimary: colors.textPrimary,
                        textSecondary: colors.textSecondary,
                    }}
                    icon={
                        <CircleIcon
                            color={colors.infoIconColor}
                            backgroundColor={colors.infoIconBg}
                        >
                            +
                        </CircleIcon>
                    }
                />
            </Box>
        </Paper>
    );
}