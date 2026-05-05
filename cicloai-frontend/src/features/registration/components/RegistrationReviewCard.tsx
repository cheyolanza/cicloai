import { Alert, Button, Divider, Paper, Stack, Typography } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useState } from 'react';
import type { FirstRaceRegistrationReview } from '@/features/registration/types/registrationReview';

interface RegistrationReviewCardProps {
  review: FirstRaceRegistrationReview;
  loading?: boolean;
  onConfirm: () => void;
  onRetryPayment: () => void;
}

/** Human-in-the-Loop review card rendered by the chat agent before insertion. */
export function RegistrationReviewCard({ review, loading = false, onConfirm, onRetryPayment }: RegistrationReviewCardProps) {
  const paymentIsValid = review.paymentStatus === 'validated';
  const [confirmClicked, setConfirmClicked] = useState(false);
  const confirmDisabled = loading || confirmClicked || !paymentIsValid;

  function handleConfirm(): void {
    setConfirmClicked(true);
    onConfirm();
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={1.5}>
        <Typography variant="h3">Revisión de inscripción</Typography>
        <Typography><strong>Carrera:</strong> {review.raceName}</Typography>
        <Typography><strong>Ciclista:</strong> {review.fullName}</Typography>
        <Typography><strong>Email:</strong> {review.email}</Typography>
        <Typography><strong>DNI:</strong> {review.dni}-{review.dniExtension}</Typography>
        <Typography><strong>Equipo:</strong> {review.bikeTeamName}</Typography>
        <Divider />
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Typography sx={{ flex: 1 }}><strong>Fecha de nacimiento:</strong> {review.birthDate}</Typography>
          <Typography sx={{ flex: 1 }}><strong>Edad:</strong> {review.age} años</Typography>
          <Typography sx={{ flex: 1 }}><strong>Categoría solicitada:</strong> {review.requestedCategory}</Typography>
          <Typography sx={{ flex: 1 }}><strong>Categoría detectada:</strong> {review.detectedCategory}</Typography>
        </Stack>
        <Alert severity={paymentIsValid ? 'success' : 'warning'}>
          {review.paymentMessage}
        </Alert>
        <Typography><strong>Monto esperado:</strong> {review.paymentExpectedAmount} {review.paymentCurrency}</Typography>
        <Typography>
          <strong>Monto detectado:</strong>{' '}
          {review.paymentExtractedAmount ? `${review.paymentExtractedAmount} ${review.paymentCurrency}` : 'No detectado'}
        </Typography>
        <Typography><strong>Banco detectado:</strong> {review.paymentBankName || 'No detectado'}</Typography>
        <Typography><strong>Fecha detectada:</strong> {review.paymentDate || 'No detectada'}</Typography>
        <Typography><strong>ID transacción:</strong> {review.paymentTransactionId || review.paymentReference}</Typography>
        <Button variant="contained" startIcon={<CheckCircleIcon />} disabled={confirmDisabled} onClick={handleConfirm}>
          {loading || confirmClicked ? 'Registrando...' : 'Confirmar inscripción'}
        </Button>
        {!paymentIsValid ? (
          <Stack spacing={1}>
            <Alert severity="info">
              El pago no fue aprobado. Puedes subir un nuevo comprobante sin perder tus datos.
            </Alert>
            <Button variant="outlined" onClick={onRetryPayment}>
              Volver a subir Pago
            </Button>
          </Stack>
        ) : null}
      </Stack>
    </Paper>
  );
}
