import { useState } from 'react';
import { Alert, Button, Stack, Typography } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { FileInputButton } from '@/components/common/FileInputButton';
import { excelService } from '@/features/agent/services/excelService';
import type { BulkRegistrationSummary } from '@/features/agent/types/registration';

interface BulkRegistrationSlideProps {
  onBack: () => void;
  onContinue: (summary: BulkRegistrationSummary) => void;
}

/**
 * Bulk registration branch. It models the UX and service contracts before real
 * Excel parsing exists, which lets backend validation evolve independently.
 */
export function BulkRegistrationSlide({ onBack, onContinue }: BulkRegistrationSlideProps) {
  const [summary, setSummary] = useState<BulkRegistrationSummary | null>(null);
  const [loading, setLoading] = useState(false);

  async function validateFile(file: File | null): Promise<void> {
    setLoading(true);
    setSummary(await excelService.validateFile(file));
    setLoading(false);
  }

  return (
    <Stack spacing={2.5} sx={{ height: '100%', justifyContent: 'center' }}>
      <Typography color="text.secondary">
        Descarga la plantilla mock y sube un archivo con las columnas: DNI, Nombre Completo, Fecha Nacimiento, Genero y Categoría.
      </Typography>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
        <Button variant="outlined" startIcon={<DownloadIcon />} onClick={() => excelService.downloadTemplate()}>
          Descargar plantilla
        </Button>
        <FileInputButton label={summary?.fileName ?? 'Subir Excel'} accept=".xlsx,.xls,.csv" onChange={validateFile} />
      </Stack>

      {loading ? <Alert severity="info">Validando archivo...</Alert> : null}
      {summary?.valid ? (
        <Alert severity="success">Archivo válido. Competidores detectados: {summary.competitorsDetected}.</Alert>
      ) : null}
      {summary && !summary.valid ? <Alert severity="warning">Selecciona un archivo válido para continuar.</Alert> : null}

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
        <Button fullWidth variant="outlined" startIcon={<ArrowBackIcon />} onClick={onBack}>
          Volver
        </Button>
        <Button
          fullWidth
          variant="contained"
          endIcon={<ArrowForwardIcon />}
          disabled={!summary?.valid}
          onClick={() => summary && onContinue(summary)}
        >
          Continuar al pago total
        </Button>
      </Stack>
    </Stack>
  );
}
