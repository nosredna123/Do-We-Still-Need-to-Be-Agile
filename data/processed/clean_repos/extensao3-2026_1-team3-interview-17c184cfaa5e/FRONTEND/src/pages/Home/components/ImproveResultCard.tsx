import { Box, Paper, Typography, Chip, Divider, useTheme } from "@mui/material";
import type { ImproveResponse } from "../../../models/improve";

interface ImproveResultCardProps {
  data: ImproveResponse;
  title?: string;
}

function getScoreLabel(score: number) {
  if (score >= 80) return "Bom potencial";
  if (score >= 60) return "Precisa melhorar";
  return "Atenção necessária";
}

export function ImproveResultCard({
  data,
  title = "Como melhorar seu currículo para esta vaga",
}: ImproveResultCardProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === "dark";

  const colors = {
    paperBg: isDark
      ? "linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(15,23,42,0.92) 100%)"
      : "linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",

    paperBorder: isDark
      ? "1px solid rgba(148, 163, 184, 0.25)"
      : "1px solid rgba(148, 163, 184, 0.30)",

    textPrimary: isDark ? "#f8fafc" : "#0f172a",
    textSecondary: isDark ? "#cbd5e1" : "#475569",
    textMuted: isDark ? "#94a3b8" : "#64748b",

    titleColor: isDark ? "#d1fae5" : "#14532d",

    cardBg: isDark
      ? "rgba(255, 255, 255, 0.045)"
      : "rgba(248, 250, 252, 0.95)",

    cardBorder: isDark
      ? "1px solid rgba(255, 255, 255, 0.09)"
      : "1px solid rgba(148, 163, 184, 0.25)",

    scoreBg: isDark
      ? "rgba(59, 130, 246, 0.10)"
      : "rgba(239, 246, 255, 0.95)",

    scoreBorder: isDark
      ? "1px solid rgba(59, 130, 246, 0.25)"
      : "1px solid rgba(59, 130, 246, 0.22)",

    scoreText: isDark ? "#bfdbfe" : "#1d4ed8",

    chipBg: isDark
      ? "rgba(148, 163, 184, 0.14)"
      : "rgba(226, 232, 240, 0.75)",

    chipBorder: isDark
      ? "1px solid rgba(148, 163, 184, 0.22)"
      : "1px solid rgba(148, 163, 184, 0.32)",

    chipText: isDark ? "#e2e8f0" : "#334155",

    divider: isDark
      ? "rgba(255,255,255,0.10)"
      : "rgba(148, 163, 184, 0.28)",

    successText: isDark ? "#bbf7d0" : "#166534",
    successBg: isDark ? "rgba(34, 197, 94, 0.14)" : "rgba(22, 163, 74, 0.10)",
    successBorder: isDark
      ? "1px solid rgba(34, 197, 94, 0.35)"
      : "1px solid rgba(22, 101, 52, 0.22)",
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
          }}
        >
          {title}
        </Typography>

        <Chip
          label={getScoreLabel(data.pontuacao_geral)}
          sx={{
            color: colors.successText,
            backgroundColor: colors.successBg,
            border: colors.successBorder,
            fontWeight: 800,
          }}
        />
      </Box>

      <Box
        sx={{
          mb: 3,
          p: 2.5,
          borderRadius: "24px",
          backgroundColor: colors.scoreBg,
          border: colors.scoreBorder,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 2,
          flexWrap: "wrap",
        }}
      >
        <Box>
          <Typography
            variant="caption"
            sx={{
              color: colors.textMuted,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 0.8,
            }}
          >
            Pontuação geral
          </Typography>

          <Typography
            variant="h3"
            sx={{
              mt: 1,
              fontWeight: 900,
              color: colors.scoreText,
              lineHeight: 1,
            }}
          >
            {data.pontuacao_geral}/100
          </Typography>
        </Box>
      </Box>

      <Box
        sx={{
          mb: 3,
          p: 2.5,
          borderRadius: "24px",
          backgroundColor: colors.cardBg,
          border: colors.cardBorder,
        }}
      >
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 800,
            mb: 1,
            color: colors.textPrimary,
          }}
        >
          Resumo diagnóstico
        </Typography>

        <Typography
          variant="body2"
          sx={{
            lineHeight: 1.7,
            color: colors.textSecondary,
          }}
        >
          {data.resumo_diagnostico}
        </Typography>
      </Box>

      <Divider sx={{ borderColor: colors.divider, mb: 3 }} />

      <Box sx={{ mb: 3 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 800,
            mb: 2,
            color: colors.textPrimary,
          }}
        >
          Melhorias por seção
        </Typography>

        {data.melhorias_por_secao.map((item, index) => (
          <Box
            key={`${item.secao}-${index}`}
            sx={{
              mb: 2,
              p: 2.5,
              borderRadius: "22px",
              backgroundColor: colors.cardBg,
              border: colors.cardBorder,
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 900,
                mb: 1.5,
                color: colors.textPrimary,
              }}
            >
              {item.secao}
            </Typography>

            <Typography
              variant="body2"
              sx={{
                fontWeight: 800,
                mb: 0.5,
                color: colors.textPrimary,
              }}
            >
              Problemas encontrados
            </Typography>

            <Box component="ul" sx={{ mt: 0, mb: 2, pl: 3 }}>
              {item.problemas.map((problema, idx) => (
                <Box component="li" key={`problema-${index}-${idx}`} sx={{ mb: 0.6 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      lineHeight: 1.6,
                      color: colors.textSecondary,
                    }}
                  >
                    {problema}
                  </Typography>
                </Box>
              ))}
            </Box>

            <Typography
              variant="body2"
              sx={{
                fontWeight: 800,
                mb: 0.5,
                color: colors.textPrimary,
              }}
            >
              Sugestões de melhoria
            </Typography>

            <Box component="ul" sx={{ mt: 0, pl: 3 }}>
              {item.sugestoes.map((sugestao, idx) => (
                <Box component="li" key={`sugestao-${index}-${idx}`} sx={{ mb: 0.6 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      lineHeight: 1.6,
                      color: colors.textSecondary,
                    }}
                  >
                    {sugestao}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        ))}
      </Box>

      <Divider sx={{ borderColor: colors.divider, mb: 3 }} />

      <Box sx={{ mb: 3 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 800,
            mb: 1.5,
            color: colors.textPrimary,
          }}
        >
          Habilidades recomendadas
        </Typography>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {data.habilidades_recomendadas.map((item, index) => (
            <Chip
              key={`habilidade-${index}`}
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

      <Box sx={{ mb: 3 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 800,
            mb: 1.5,
            color: colors.textPrimary,
          }}
        >
          Palavras-chave faltantes
        </Typography>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {data.palavras_chave_faltantes.map((item, index) => (
            <Chip
              key={`palavra-chave-${index}`}
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

      <Box
        sx={{
          p: 2.5,
          borderRadius: "24px",
          backgroundColor: colors.cardBg,
          border: colors.cardBorder,
        }}
      >
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 800,
            mb: 1,
            color: colors.textPrimary,
          }}
        >
          Ações prioritárias
        </Typography>

        <Box component="ol" sx={{ mt: 0, mb: 0, pl: 3 }}>
          {data.acoes_prioritarias.map((item, index) => (
            <Box component="li" key={`acao-${index}`} sx={{ mb: 0.8 }}>
              <Typography
                variant="body2"
                sx={{
                  lineHeight: 1.7,
                  color: colors.textSecondary,
                }}
              >
                {item}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Paper>
  );
}