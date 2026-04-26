import { Button, Stack, Typography } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';

interface ThankYouSlideProps {
  onHome: () => void;
}

/**
 * Editable completion slide. Future phases can inject event-specific messages
 * or verification status here without affecting payment or registration steps.
 */
export function ThankYouSlide({ onHome }: ThankYouSlideProps) {
  return (
    <Stack spacing={2.5} sx={{ height: '100%', justifyContent: 'center', textAlign: 'center', alignItems: 'center' }}>
      <Typography variant="h1">Gracias por completar tu inscripción.</Typography>
      <Typography color="text.secondary" sx={{ maxWidth: 520 }}>
        Te enviaremos un correo de verificación cuando el equipo organizador confirme tus datos y comprobante.
      </Typography>
      <Button variant="contained" startIcon={<HomeIcon />} onClick={onHome}>
        Volver al inicio
      </Button>
    </Stack>
  );
}
