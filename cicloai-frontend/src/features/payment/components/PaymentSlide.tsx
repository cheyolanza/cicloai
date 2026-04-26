import { useState } from 'react';
import { Alert, Box, Button, Stack, Typography } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ReplayIcon from '@mui/icons-material/Replay';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import VerifiedIcon from '@mui/icons-material/Verified';
import { FileInputButton } from '@/components/common/FileInputButton';
import { paymentService } from '@/features/payment/services/paymentService';
import type { PaymentValidationResult } from '@/features/payment/types/payment';

interface PaymentSlideProps {
  amount: number;
  currency: string;
  qrImage?: string | null;
  onBack: () => void;
  onValidated: () => void;
}

/**
 * Payment slide for all registration branches. The QR source is currently a
 * static asset, but the service boundary is already shaped for backend-owned
 * payment intents and OCR/payment validation.
 */
export function PaymentSlide({ amount, currency, qrImage, onBack, onValidated }: PaymentSlideProps) {
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

    if (validation.status === 'approved') {
      setPaymentStatus('approved');
      onValidated();
      return;
    }

    setPaymentStatus('rejected');
    setErrorMessage(validation.message);
  }

  return (
    <Stack spacing={2} sx={{ height: '100%', justifyContent: 'center' }}>
      <Typography variant="h3">
        Monto estimado: {amount} {currency}
      </Typography>
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
            <Button variant="contained" color="error" startIcon={<ReplayIcon />} onClick={resetForRetry}>
              Subir Pago Nuevamente
            </Button>
          </Stack>
        </Box>
      ) : null}

      {paymentStatus !== 'rejected' ? (
        <>
          <Box
            sx={{
              width: 190,
              height: 190,
              border: '1px dashed',
              borderColor: 'divider',
              borderRadius: 1,
              display: 'grid',
              placeItems: 'center',
              bgcolor: '#FBFCFC',
              alignSelf: 'center',
              overflow: 'hidden',
            }}
          >
            {qrFailed ? (
              <Typography align="center" color="text.secondary" sx={{ px: 2 }}>
                Placeholder QR: agrega public/images/qr_payment.png
              </Typography>
            ) : (
              <Box
                component="img"
                src={qrImage ?? paymentService.getStaticQrUrl()}
                alt="QR de pago"
                onError={() => setQrFailed(true)}
                sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            )}
          </Box>
          <Typography variant="body2" color="text.secondary" align="center">
            QR cargado desde la carrera activa. En una fase posterior podrá reemplazarse por un QR dinámico por inscripción.
          </Typography>
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
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <Button fullWidth variant="outlined" startIcon={<ArrowBackIcon />} onClick={onBack}>
              Volver
            </Button>
            <Button fullWidth variant="contained" startIcon={<VerifiedIcon />} disabled={loading || paymentStatus === 'uploading'} onClick={validatePayment}>
              {paymentStatus === 'uploading' || loading ? 'Validando...' : 'Validar pago'}
            </Button>
          </Stack>
        </>
      ) : null}
    </Stack>
  );
}
