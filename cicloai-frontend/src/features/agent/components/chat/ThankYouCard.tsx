import { Button, Paper, Stack, Typography } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

interface ThankYouCardProps {
  onHome: () => void;
  onRestart: () => void;
}

/** Editable final chat card shown when the guided flow completes. */
export function ThankYouCard({ onHome, onRestart }: ThankYouCardProps) {
  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2} alignItems="flex-start">
        <Typography variant="h3">Gracias por completar tu inscripción.</Typography>
        <Typography color="text.secondary">
          Te enviaremos un correo de verificación cuando el equipo organizador confirme tus datos y comprobante.
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Button variant="contained" startIcon={<HomeIcon />} onClick={onHome}>
            IR al inicio
          </Button>
          <Button variant="outlined" startIcon={<RestartAltIcon />} onClick={onRestart}>
            Volver a inscribir
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );
}
