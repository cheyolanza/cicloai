import type { BulkRegistrationSummary } from '@/features/agent/types/registration';
import { appConfig } from '@/config/env';
import { tokenService } from '@/features/access/services/tokenService';

export interface ExcelService {
  downloadTemplate(): Promise<void>;
  validateFile(file: File | null): Promise<BulkRegistrationSummary>;
}

interface BulkRegistrationApiResponse {
  inserted_competitors: number;
  unit_cost: number;
  currency: string;
  total_amount: number;
  message: string;
}

function requireAccessToken(): string {
  const token = tokenService.getToken();
  if (!token) throw new Error('Operación no permitida. El usuario debe validarse.');
  return token;
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail ?? `HTTP ${response.status}: ${response.statusText}`;
  } catch {
    return `HTTP ${response.status}: ${response.statusText}`;
  }
}

/** Backend boundary for bulk registration template download and upload. */
export const excelService: ExcelService = {
  async downloadTemplate(): Promise<void> {
    const response = await fetch(`${appConfig.apiBaseUrl}/registrations/bulk/template`, {
      headers: { Authorization: `Bearer ${requireAccessToken()}` },
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'plantilla-inscripcion-masiva-cicloai.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  },
  async validateFile(file: File | null): Promise<BulkRegistrationSummary> {
    if (!file) {
      return { fileName: '', competitorsDetected: 0, valid: false };
    }

    const form = new FormData();
    form.set('template_file', file);

    const response = await fetch(`${appConfig.apiBaseUrl}/registrations/bulk/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${requireAccessToken()}` },
      body: form,
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    const result = (await response.json()) as BulkRegistrationApiResponse;
    return {
      fileName: file.name,
      competitorsDetected: result.inserted_competitors,
      valid: true,
      insertedCompetitors: result.inserted_competitors,
      unitCost: result.unit_cost,
      currency: result.currency,
      totalAmount: result.total_amount,
      message: result.message,
    };
  },
};
