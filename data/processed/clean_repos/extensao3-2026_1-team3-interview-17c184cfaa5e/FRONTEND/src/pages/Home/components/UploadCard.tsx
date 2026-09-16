import { Box, Button, Paper, Typography } from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";

type Props = {
    arquivo: File | null;
    onFileChange: (file: File | null) => void;
};

export default function UploadCard({ arquivo, onFileChange }: Props) {
    return (
        <Paper
            elevation={0}
            sx={{
                p: 5,
                borderRadius: "32px",
                border: "1px solid #edf2f7",
                textAlign: "center",
                minHeight: 454,
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
                Currículo
            </Typography>

            <Box sx={{ color: "#86bba7", mb: 3 }}>
                <UploadFileIcon sx={{ fontSize: 72 }} />
            </Box>

            <Typography
                variant="h6"
                sx={{
                    mb: 1.5,
                    fontSize: "1.2rem",
                    fontWeight: 500,
                }}
            >
                Enviar Currículo
            </Typography>

            <Typography
                variant="body2"
                sx={{
                    color: "text.secondary",
                    mb: 5,
                    fontSize: "0.95rem",
                }}
            >
                (Formato PDF)
            </Typography>

            <Button
                variant="contained"
                component="label"
                fullWidth
                sx={{
                    backgroundColor: "#a7e5cb",
                    color: "#2d5c48",
                    fontWeight: 700,
                    py: 2,
                    borderRadius: "20px",
                    boxShadow: "none",
                    fontSize: "1rem",
                    textTransform: "uppercase",
                    "&:hover": {
                        backgroundColor: "#92dabf",
                        boxShadow: "none",
                    },
                }}
            >
                {arquivo ? arquivo.name : "Upload File"}
                <input
                    hidden
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) => onFileChange(e.target.files?.[0] || null)}
                />
            </Button>
        </Paper>
    );
}