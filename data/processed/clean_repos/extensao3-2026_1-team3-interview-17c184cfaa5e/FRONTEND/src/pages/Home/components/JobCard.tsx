import {
    Box,
    Button,
    CircularProgress,
    Paper,
    Typography,
} from "@mui/material";
import DescriptionIcon from "@mui/icons-material/Description";

type Props = {
    jobDescription: string;
    onOpenJobDescription: () => void;
    loading: boolean;
};

export default function JobCard({
    jobDescription,
    onOpenJobDescription,
    loading,
}: Props) {
    const hasJobDescription = jobDescription.trim().length > 0;

    return (
        <Paper
            elevation={0}
            sx={{
                p: 5,
                borderRadius: "32px",
                border: "1px solid #edf2f7",
                textAlign: "center",
                minHeight: 430,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                backgroundColor: "background.paper",
                borderColor: "divider",
                color: "text.primary",
            }}
        >
            <Typography
                variant="h6"
                sx={{
                    fontWeight: 600,
                    mb: 3,
                    fontSize: "2rem",
                }}
            >
                Vaga
            </Typography>

            <Box sx={{ color: "#758ca3", mb: 3 }}>
                <DescriptionIcon sx={{ fontSize: 72 }} />
            </Box>

            <Box sx={{ textAlign: "left", mt: 1 }}>
                <Typography
                    variant="body2"
                    sx={{
                        fontWeight: 500,
                        mb: 1.5,
                        fontSize: "1rem",
                    }}
                >
                    Descrição textual da vaga
                </Typography>

                <Button
                    variant="contained"
                    fullWidth
                    onClick={onOpenJobDescription}
                    disabled={loading}
                    sx={{
                        mb: 3,
                        backgroundColor: "#ffffff",
                        color: "#163a63",
                        fontWeight: 600,
                        py: 2,
                        borderRadius: "20px",
                        boxShadow: "none",
                        border: "1px solid #dbe3ef",
                        textTransform: "none",
                        "&:hover": {
                            backgroundColor: "#f8fafc",
                            boxShadow: "none",
                        },
                    }}
                >
                    {loading ? (
                        <>
                            <CircularProgress
                                size={20}
                                sx={{ mr: 1, color: "#163a63" }}
                            />
                            Analisando...
                        </>
                    ) : hasJobDescription ? (
                        "Editar texto da vaga"
                    ) : (
                        "Adicionar texto da vaga"
                    )}
                </Button>

                {hasJobDescription && (
                    <Box
                        sx={{
                            p: 2,
                            borderRadius: "16px",
                            backgroundColor: "#f8fafc",
                            border: "1px solid #dbe3ef",
                            mb: 2,
                        }}
                    >
                        <Typography
                            variant="body2"
                            sx={{
                                fontWeight: 600,
                                mb: 1,
                                color: "#163a63",
                            }}
                        >
                            Texto da vaga informado
                        </Typography>

                        <Typography
                            variant="body2"
                            sx={{
                                color: "#475569",
                                display: "-webkit-box",
                                WebkitLineClamp: 4,
                                WebkitBoxOrient: "vertical",
                                overflow: "hidden",
                                lineHeight: 1.6,
                            }}
                        >
                            {jobDescription}
                        </Typography>
                    </Box>
                )}

                <Typography
                    variant="body2"
                    sx={{
                        color: "text.secondary",
                        fontSize: "0.9rem",
                        lineHeight: 1.5,
                    }}
                >
                    Cole a descrição da vaga para que o sistema compare os requisitos com o currículo enviado.
                </Typography>
            </Box>
        </Paper>
    );
}