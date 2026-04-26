import { useState } from 'react';
import { Alert, Box, Button, Paper, Stack, Typography } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ReplayIcon from '@mui/icons-material/Replay';
import VerifiedIcon from '@mui/icons-material/Verified';
import { FileInputButton } from '@/components/common/FileInputButton';
import { paymentService } from '@/features/payment/services/paymentService';
import type { PaymentValidationResult } from '@/features/payment/types/payment';

interface PaymentCardProps {
  amount: number;
  currency: string;
  qrImage?: string | null;
  onValidated: (proof: File) => void;
}

/** Rich chat card for payment QR and proof upload. */
export function PaymentCard({ amount, currency, qrImage, onValidated }: PaymentCardProps) {
  const [proof, setProof] = useState<File | null>(null);
  const [result, setResult] = useState<PaymentValidationResult | null>(null);
  const [qrFailed, setQrFailed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'uploading' | 'approved' | 'rejected'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const paymentPrompt = 'Pago: sube una imagen del comprobante para continuar.';

  function resetForRetry(): void {
    setPaymentStatus('idle');
    setErrorMessage(null);
    setResult(null);
    setLoading(false);
    setProof(null);
    setQrFailed(false);
  }

  async function validatePayment(): Promise<void> {
    if (!proof) {
      setPaymentStatus('rejected');
      setErrorMessage('Debes subir un comprobante para continuar.');
      setResult({
        status: 'rejected',
        valid: false,
        reference: '',
        message: 'Debes subir un comprobante para continuar.',
      });
      return;
    }

    setPaymentStatus('uploading');
    setLoading(true);
    const validation = await paymentService.validateProof(proof);
    setResult(validation);
    setLoading(false);

    if (validation.status === 'approved' && proof) {
      setPaymentStatus('approved');
      onValidated(proof);
      return;
    }

    setPaymentStatus('rejected');
    setErrorMessage(validation.message);
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2} alignItems="center">
        <Typography variant="h3">Monto estimado: {amount} {currency}</Typography>

        {paymentStatus === 'rejected' ? (
          <Box
            sx={{
              width: '100%',
              border: '1px solid',
              borderColor: 'error.main',
              bgcolor: 'rgba(211, 47, 47, 0.06)',
              borderRadius: 2,
              p: 2,
            }}
          >
            <Stack spacing={1.5} alignItems="center" textAlign="center">
              <ErrorOutlineIcon color="error" fontSize="large" />
              <Typography variant="h3" color="error.main">
                Pago fallido
              </Typography>
              <Alert severity="error" sx={{ width: '100%' }}>
                {errorMessage ?? result?.message ?? 'El pago no pudo validarse.'}
              </Alert>
              <Button
                variant="contained"
                color="error"
                startIcon={<ReplayIcon />}
                onClick={resetForRetry}
              >
                Subir Pago Nuevamente
              </Button>
            </Stack>
          </Box>
        ) : null}

        {paymentStatus !== 'rejected' ? (
          <>
            <Box
              sx={{
                width: 220,
                height: 220,
                border: '1px dashed',
                borderColor: 'divider',
                borderRadius: 1,
                display: 'grid',
                placeItems: 'center',
                bgcolor: '#FBFCFC',
                overflow: 'hidden',
              }}
            >
              {qrFailed || !qrImage ? (
                <Typography align="center" color="text.secondary" sx={{ px: 2 }}>
                  QR no disponible. Revisa la carrera activa.
                </Typography>
              ) : (
                <Box
                  component="img"
                  src={qrImage}
                  alt="QR de pago"
                  onError={() => setQrFailed(true)}
                  sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              )}
            </Box>
            <FileInputButton
              label={proof?.name ?? 'Subir comprobante de pago'}
              accept="image/png,image/jpeg,image/webp"
              onChange={setProof}
            />
            {paymentStatus === 'approved' ? (
              <Alert severity="success" icon={<CheckCircleIcon />}>
                El pago fue validado correctamente.
              </Alert>
            ) : null}
            {paymentStatus === 'idle' ? (
              <Alert severity="info" sx={{ width: '100%' }}>
                {paymentPrompt}
              </Alert>
            ) : null}
            <Button variant="contained" startIcon={<VerifiedIcon />} disabled={loading || paymentStatus === 'uploading'} onClick={validatePayment}>
              {paymentStatus === 'uploading' || loading ? 'Validando...' : 'Validar pago'}
            </Button>
          </>
        ) : null}
      </Stack>
    </Paper>
  );
}
