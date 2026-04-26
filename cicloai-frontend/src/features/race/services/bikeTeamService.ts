import { tokenService } from '@/features/access/services/tokenService';
import type { BikeTeam } from '@/features/race/types/bikeTeam';
import { httpClient } from '@/services/http/httpClient';

interface BikeTeamApiResponse {
  id: string;
  name: string;
  active: boolean;
  manager_name?: string | null;
  contact_phone?: string | null;
  facebook_page?: string | null;
  picture_url?: string | null;
}

export interface BikeTeamService {
  getActiveTeams(): Promise<BikeTeam[]>;
}

/**
 * Reads active teams from FastAPI using the CAPTCHA-issued Bearer Token.
 * Sorting and filtering live in the backend so all clients share the same
 * catalog behavior.
 */
export const bikeTeamService: BikeTeamService = {
  async getActiveTeams(): Promise<BikeTeam[]> {
    const accessToken = tokenService.getToken();

    if (!accessToken) {
      throw new Error('Operación no permitida. El usuario debe validarse.');
    }

    const teams = await httpClient<BikeTeamApiResponse[]>('/bike-teams/active', {
      authToken: accessToken,
    });

    return teams.map((team) => ({
      id: team.id,
      name: team.name,
      active: team.active,
      managerName: team.manager_name ?? null,
      contactPhone: team.contact_phone ?? null,
      facebookPage: team.facebook_page ?? null,
      pictureUrl: team.picture_url ?? null,
    }));
  },
};
