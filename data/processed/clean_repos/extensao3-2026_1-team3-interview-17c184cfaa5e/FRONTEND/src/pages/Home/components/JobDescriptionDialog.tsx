import { useEffect, useState } from "react";
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Typography,
} from "@mui/material";

interface JobDescriptionDialogProps {
    open: boolean;
    initialValue?: string;
    loading?: boolean;
    onClose: () => void;
    onConfirm: (jobDescription: string) => void;
}

export function JobDescriptionDialog({
    open,
    initialValue = "",
    loading = false,
    onClose,
    onConfirm,
}: JobDescriptionDialogProps) {
    const [value, setValue] = useState(initialValue);

    useEffect(() => {
        if (open) {
            setValue(initialValue);
        }
    }, [open, initialValue]);

    const handleConfirm = () => {
        const texto = value.trim();

        if (!texto) return;

        onConfirm(texto);
    };

    return (
        <Dialog open={open} onClose={loading ? undefined : onClose} fullWidth maxWidth="md">
            <DialogTitle>Texto da vaga</DialogTitle>

            <DialogContent>
                <Typography variant="body2" sx={{ mb: 2, color: "text.secondary" }}>
                    Cole abaixo a descrição completa da vaga para que o sistema compare com o currículo enviado.
                </Typography>

                <TextField
                    autoFocus
                    fullWidth
                    multiline
                    minRows={8}
                    value={value}
                    disabled={loading}
                    onChange={(event) => setValue(event.target.value)}
                    placeholder="Cole aqui a descrição da vaga..."
                />
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2 }}>
                <Button onClick={onClose} disabled={loading}>
                    Cancelar
                </Button>

                <Button
                    variant="contained"
                    onClick={handleConfirm}
                    disabled={loading || !value.trim()}
                >
                    Confirmar e analisar
                </Button>
            </DialogActions>
        </Dialog>
    );
}