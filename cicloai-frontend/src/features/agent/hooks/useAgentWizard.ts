import { useMemo, useState } from 'react';
import type { Race } from '@/features/race/types/race';
import type {
  AgentStep,
  BulkRegistrationSummary,
  ExistingUser,
  NewUserRegistration,
  RegistrationType,
} from '@/features/agent/types/registration';
import { paymentService } from '@/features/payment/services/paymentService';

export interface AgentWizardState {
  step: AgentStep;
  registrationType: RegistrationType | null;
  newUser: NewUserRegistration | null;
  existingUser: ExistingUser | null;
  bulkSummary: BulkRegistrationSummary | null;
  amount: number;
  competitorsCount: number;
}

/**
 * Local state machine for Fase 1. The hook exposes intention-based commands
 * instead of raw setters so later phases can move transitions to a backend
 * workflow or agent state machine without changing every slide.
 */
export function useAgentWizard(race: Race | null) {
  const [step, setStep] = useState<AgentStep>('race-selection');
  const [registrationType, setRegistrationType] = useState<RegistrationType | null>(null);
  const [newUser, setNewUser] = useState<NewUserRegistration | null>(null);
  const [existingUser, setExistingUser] = useState<ExistingUser | null>(null);
  const [bulkSummary, setBulkSummary] = useState<BulkRegistrationSummary | null>(null);

  const competitorsCount = registrationType === 'bulk' ? bulkSummary?.competitorsDetected ?? 0 : 1;
  const amount = useMemo(() => {
    if (!race || !registrationType) return 0;
    return paymentService.calculateAmount({
      registrationType,
      competitorsCount,
      unitPrice: race.inscriptionPrice,
    });
  }, [competitorsCount, race, registrationType]);

  function chooseRegistrationType(type: RegistrationType): void {
    setRegistrationType(type);
    setStep(type === 'new' ? 'new-user' : type === 'existing' ? 'existing-user' : 'bulk-registration');
  }

  function backToRaceSelection(): void {
    setStep('race-selection');
  }

  function continueWithNewUser(registration: NewUserRegistration): void {
    setNewUser(registration);
    setStep('payment');
  }

  function continueWithExistingUser(user: ExistingUser): void {
    setExistingUser(user);
    setStep('payment');
  }

  function continueWithBulk(summary: BulkRegistrationSummary): void {
    setBulkSummary(summary);
    setStep('payment');
  }

  function finish(): void {
    setStep('thanks');
  }

  function reset(): void {
    setRegistrationType(null);
    setNewUser(null);
    setExistingUser(null);
    setBulkSummary(null);
    setStep('race-selection');
  }

  return {
    state: { step, registrationType, newUser, existingUser, bulkSummary, amount, competitorsCount },
    chooseRegistrationType,
    backToRaceSelection,
    continueWithNewUser,
    continueWithExistingUser,
    continueWithBulk,
    finish,
    reset,
  };
}
