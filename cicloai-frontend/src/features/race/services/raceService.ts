import type { Race } from '@/features/race/types/race';
import { tokenService } from '@/features/access/services/tokenService';
import { httpClient } from '@/services/http/httpClient';

export interface RaceService {
  getEnabledRace(): Promise<Race | null>;
}

interface ActiveBikeRaceResponse {
  id?: string;
  name?: string;
  location_name?: string;
  location?: string | null;
  year?: number;
  date_of_race?: string | null;
  status?: 'active' | 'deactive';
  cost?: number;
  currency?: 'BOB' | 'USD';
  qr_image?: string | null;
  message?: string;
}

/**
 * Race data source backed by FastAPI.
 * This is the first frontend service moved off mocks: it requires the
 * CAPTCHA-issued Bearer Token and maps backend race fields into the wizard's
 * current UI model.
 */
export const raceService: RaceService = {
  async getEnabledRace(): Promise<Race | null> {
    const accessToken = tokenService.getToken();

    if (!accessToken) {
      throw new Error('Operación no permitida. El usuario debe validarse.');
    }

    const response = await httpClient<ActiveBikeRaceResponse>('/bike-races/active', {
      authToken: accessToken,
    });

    if (response.message || !response.id || !response.name) {
      return null;
    }

    return {
      id: response.id,
      name: response.name,
      date: response.date_of_race ?? undefined,
      description: response.location_name
        ? `${response.location_name}${response.year ? ` - Gestion ${response.year}` : ''}`
        : undefined,
      inscriptionPrice: response.cost ?? 0,
      currency: response.currency ?? 'BOB',
      paymentQrImage: response.qr_image ?? null,
    };
  },
};
