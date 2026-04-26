export type RegistrationType = 'new' | 'existing' | 'bulk' | 'chat';

export interface NewUserRegistration {
  dni: string;
  dniExtension: string;
  fullName: string;
  email: string;
  birthDate: string;
  gender: string;
  category: string;
  team: string;
}

export interface ExistingUser {
  id: string;
  dni: string;
  fullName: string;
  birthDate: string;
  team: string;
}

export interface BulkRegistrationSummary {
  fileName: string;
  competitorsDetected: number;
  valid: boolean;
  insertedCompetitors?: number;
  unitCost?: number;
  currency?: string;
  totalAmount?: number;
  message?: string;
}

export type AgentStep = 'race-selection' | 'new-user' | 'existing-user' | 'bulk-registration' | 'payment' | 'thanks';
