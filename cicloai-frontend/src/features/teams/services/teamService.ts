import { appConfig } from '@/config/env';
import { tokenService } from '@/features/access/services/tokenService';
import type { CyclingTeam } from '@/features/teams/types/team.types';

interface CyclingTeamApiResponse {
  id: string;
  name: string;
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

/** Team catalog service for the existing-biker review flow. */
export const teamService = {
  async getActiveTeams(): Promise<CyclingTeam[]> {
    const response = await fetch(`${appConfig.apiBaseUrl}/cycling-teams/active`, {
      headers: { Authorization: `Bearer ${requireAccessToken()}` },
    });

    if (!response.ok) throw new Error(await readError(response));

    const payload = (await response.json()) as CyclingTeamApiResponse[];
    return payload.map((team) => ({ id: team.id, name: team.name }));
  },
};
