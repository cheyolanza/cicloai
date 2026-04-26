import { Alert, Box, Button, Card, CardContent, Stack, Typography } from '@mui/material';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import { BrandMark } from '@/components/common/BrandMark';
import { FullScreenFlowLayout } from '@/components/layout/FullScreenFlowLayout';
import { RecaptchaEnterpriseWidget } from '@/features/access/components/RecaptchaEnterpriseWidget';
import { useHumanValidation } from '@/features/access/hooks/useHumanValidation';

export function AccessPage() {
  const { recaptchaToken, setRecaptchaToken, loading, error, validate } = useHumanValidation();

  return (
    <FullScreenFlowLayout maxWidth="sm">
      <Stack sx={{ height: '100%', justifyContent: 'center' }} spacing={3}>
        <BrandMark />
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h1" gutterBottom>
                  Bienvenido a CicloAI
                </Typography>
                <Typography color="text.secondary">
                  Antes de iniciar tu inscripción validaremos que eres una persona. Luego te guiaremos por el agente de registro.
                </Typography>
              </Box>

              <RecaptchaEnterpriseWidget action="LOGIN" onTokenChange={setRecaptchaToken} />

              {error ? <Alert severity="warning">{error}</Alert> : null}

              <Button
                id="btnAcceder"
                size="large"
                variant="contained"
                startIcon={<ShieldOutlinedIcon />}
                disabled={loading || !recaptchaToken}
                onClick={validate}
              >
                {loading ? 'Validando...' : 'Validar y continuar'}
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </FullScreenFlowLayout>
  );
}
