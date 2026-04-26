import { useState } from 'react';
import { Alert, Button, Paper, Stack, Typography } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { FileInputButton } from '@/components/common/FileInputButton';
import { excelService } from '@/features/agent/services/excelService';
import type { BulkRegistrationSummary } from '@/features/agent/types/registration';
import { AccessRequiredAlert } from '@/components/common/AccessRequiredAlert';
import { isAccessRequiredMessage } from '@/components/common/accessRequired';

interface BulkRegistrationCardProps {
  onSubmit: (summary: BulkRegistrationSummary) => void;
}

/** Embedded card for bulk registration file validation. */
export function BulkRegistrationCard({ onSubmit }: BulkRegistrationCardProps) {
  const [summary, setSummary] = useState<BulkRegistrationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function downloadTemplate(): Promise<void> {
    try {
      setError(null);
      await excelService.downloadTemplate();
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : 'No pudimos descargar la plantilla.');
    }
  }

  async function validateFile(file: File | null): Promise<void> {
    setLoading(true);
    setError(null);

    try {
      setSummary(await excelService.validateFile(file));
    } catch (currentError) {
      setSummary(null);
      setError(currentError instanceof Error ? currentError.message : 'No pudimos validar la plantilla.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2}>
        <Typography variant="h3">Inscripción masiva</Typography>
        <Typography color="text.secondary">
          La plantilla debe incluir DNI, Nombre Completo, Fecha Nacimiento, Genero y Categoria.
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Button variant="outlined" startIcon={<DownloadIcon />} onClick={() => void downloadTemplate()}>
            Descargar plantilla
          </Button>
          <FileInputButton label={summary?.fileName ?? 'Subir plantilla CSV'} accept=".csv" onChange={validateFile} />
        </Stack>
        {loading ? <Alert severity="info">Validando archivo...</Alert> : null}
        {summary?.valid ? (
          <Alert severity="success">
            {summary.message} Insertados: {summary.insertedCompetitors}. Total esperado: {summary.totalAmount} {summary.currency}.
          </Alert>
        ) : null}
        {summary && !summary.valid ? <Alert severity="warning">Selecciona un archivo válido para continuar.</Alert> : null}
        {error ? (
          isAccessRequiredMessage(error) ? <AccessRequiredAlert message={error} /> : <Alert severity="warning">{error}</Alert>
        ) : null}
        <Button
          variant="contained"
          endIcon={<ArrowForwardIcon />}
          disabled={!summary?.valid}
          onClick={() => summary && onSubmit(summary)}
        >
          Enviar archivo al agente
        </Button>
      </Stack>
    </Paper>
  );
}
