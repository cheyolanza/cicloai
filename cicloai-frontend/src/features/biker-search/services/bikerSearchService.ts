import { appConfig } from '@/config/env';
import { tokenService } from '@/features/access/services/tokenService';
import type {
  BikerLookupActionRequest,
  BikerLookupActionResult,
  BikerSearchResult,
} from '@/features/biker-search/types/bikerSearch.types';

interface BikerSearchApiResult {
  id: string;
  full_name: string;
  dni: string;
  birth_date: string;
  cellphone?: string | null;
  team_name?: string | null;
  category: string;
  last_registered_race?: { id: string; name: string } | null;
}

interface BikerSearchApiResponse {
  status: 'found' | 'not_found';
  message?: string;
  results?: BikerSearchApiResult[];
}

interface BikerLookupActionApiResponse {
  status: 'completed';
  message: string;
  biker: {
    id: string;
    full_name: string;
    team_name: string;
  };
  next_action: 'CONTINUE_TO_PAYMENT_LATER';
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

function mapResult(result: BikerSearchApiResult): BikerSearchResult {
  return {
    id: result.id,
    fullName: result.full_name,
    dni: result.dni,
    birthDate: result.birth_date,
    cellphone: result.cellphone,
    teamName: result.team_name,
    category: result.category,
    lastRegisteredRace: result.last_registered_race,
  };
}

/** FastAPI boundary for existing-biker lookup and team update actions. */
export const bikerSearchService = {
  async searchByName(name: string): Promise<{ status: 'found'; results: BikerSearchResult[] } | { status: 'not_found'; message: string }> {
    const response = await fetch(`${appConfig.apiBaseUrl}/bikers/search?name=${encodeURIComponent(name)}`, {
      headers: { Authorization: `Bearer ${requireAccessToken()}` },
    });

    if (!response.ok) throw new Error(await readError(response));

    const payload = (await response.json()) as BikerSearchApiResponse;
    if (payload.status === 'not_found') {
      return { status: 'not_found', message: payload.message ?? 'No se encontraron ciclistas con ese nombre.' };
    }

    return { status: 'found', results: (payload.results ?? []).map(mapResult) };
  },

  async registerLookupAction(bikerId: string, request: BikerLookupActionRequest): Promise<BikerLookupActionResult> {
    const response = await fetch(`${appConfig.apiBaseUrl}/bikers/${bikerId}/lookup-action`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${requireAccessToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        bike_race_id: request.bikeRaceId ?? null,
        searched_name: request.searchedName,
        new_team_name: request.newTeamName,
        confirm_action: request.confirmAction,
      }),
    });

    if (!response.ok) throw new Error(await readError(response));

    const payload = (await response.json()) as BikerLookupActionApiResponse;
    return {
      status: payload.status,
      message: payload.message,
      biker: {
        id: payload.biker.id,
        fullName: payload.biker.full_name,
        teamName: payload.biker.team_name,
      },
      nextAction: payload.next_action,
    };
  },
};
