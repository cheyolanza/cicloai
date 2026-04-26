import type { ExistingUser } from '@/features/agent/types/registration';

export interface UserLookupService {
  searchByName(name: string): Promise<ExistingUser | null>;
}

const existingUsers: ExistingUser[] = [
  {
    id: 'u-001',
    dni: '4588123',
    fullName: 'Jose Miguel Lanza',
    birthDate: '1990-08-12',
    team: 'CicloAI Team',
  },
  {
    id: 'u-002',
    dni: '6632109',
    fullName: 'Maria Fernanda Rojas',
    birthDate: '1994-03-21',
    team: 'Independiente',
  },
];

/**
 * Lookup service isolated from the wizard so the search strategy can evolve:
 * exact name in mocks, fuzzy backend search, or LLM-assisted matching later.
 */
export const userLookupService: UserLookupService = {
  async searchByName(name: string): Promise<ExistingUser | null> {
    await new Promise((resolve) => window.setTimeout(resolve, 500));
    const normalizedName = name.trim().toLowerCase();
    return existingUsers.find((user) => user.fullName.toLowerCase().includes(normalizedName)) ?? null;
  },
};
