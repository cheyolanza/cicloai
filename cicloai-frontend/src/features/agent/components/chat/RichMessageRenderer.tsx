import { Alert, Box, Button, Chip, Stack, Typography } from '@mui/material';
import type { AgentUiAction } from '@/features/agent/types/conversation';
import type { Race } from '@/features/race/types/race';
import type {
  BulkRegistrationSummary,
  NewUserRegistration,
  RegistrationType,
} from '@/features/agent/types/registration';
import { AgentOptionCard } from '@/features/agent/components/chat/AgentOptionCard';
import { NewUserRegistrationCard } from '@/features/registration/components/NewUserRegistrationCard';
import { BikerSearchCard } from '@/features/biker-search/components/BikerSearchCard';
import { BulkRegistrationCard } from '@/features/registration/components/BulkRegistrationCard';
import { PaymentCard } from '@/features/payment/components/PaymentCard';
import { ThankYouCard } from '@/features/agent/components/chat/ThankYouCard';
import { RegistrationReviewCard } from '@/features/registration/components/RegistrationReviewCard';
import type { FirstRaceRegistrationReview } from '@/features/registration/types/registrationReview';
import type { BikerLookupActionResult } from '@/features/biker-search/types/bikerSearch.types';

interface RichMessageRendererProps {
  action?: AgentUiAction;
  amount: number;
  race: Race | null;
  registrationReview: FirstRaceRegistrationReview | null;
  confirmationLoading: boolean;
  onHome: () => void;
  onRestart: () => void;
  onOptionSelect: (type: RegistrationType) => void;
  onBulkSubmit: (summary: BulkRegistrationSummary) => void;
  onExistingUserSubmit: (result: BikerLookupActionResult) => void;
  onNewUserSubmit: (registration: NewUserRegistration) => void;
  onPaymentValidated: (proof: File) => void;
  onRegistrationConfirm: () => void;
}

/**
 * Maps agent UI actions to embedded rich cards.
 * This isolates presentation of agent-directed actions from the conversation
 * state machine and mirrors the future backend `ui_action` contract.
 */
export function RichMessageRenderer({
  action,
  amount,
  race,
  registrationReview,
  confirmationLoading,
  onHome,
  onRestart,
  onOptionSelect,
  onBulkSubmit,
  onExistingUserSubmit,
  onNewUserSubmit,
  onPaymentValidated,
  onRegistrationConfirm,
}: RichMessageRendererProps) {
  if (!action) return null;

  if (action.type === 'SHOW_EMPTY_RACE_MESSAGE') {
    return <Alert severity="info" sx={{ mt: 1 }}>No hay carreras habilitadas actualmente.</Alert>;
  }

  if (action.type === 'SHOW_OPTIONS') {
    return (
      <Box sx={{ mt: 1.5 }}>
        {race ? (
          <Stack spacing={1} sx={{ mb: 1.5 }}>
            <Chip label="Carrera habilitada" color="primary" sx={{ alignSelf: 'flex-start' }} />
            <Typography variant="h3">{race.name}</Typography>
            <Typography color="text.secondary">{race.description}</Typography>
            <Typography fontWeight={700}>Costo: {race.inscriptionPrice} {race.currency}</Typography>
          </Stack>
        ) : null}
        <AgentOptionCard options={action.options} onSelect={onOptionSelect} />
      </Box>
    );
  }

  if (action.type === 'SHOW_FORM' && action.form === 'NEW_USER_REGISTRATION') {
    return <Box sx={{ mt: 1.5 }}><NewUserRegistrationCard onSubmit={onNewUserSubmit} /></Box>;
  }

  if (action.type === 'SHOW_FORM' && action.form === 'EXISTING_USER_SEARCH') {
    return <Box sx={{ mt: 1.5 }}><BikerSearchCard bikeRaceId={race?.id} onCompleted={onExistingUserSubmit} /></Box>;
  }

  if (action.type === 'SHOW_FORM' && action.form === 'BULK_REGISTRATION') {
    return <Box sx={{ mt: 1.5 }}><BulkRegistrationCard onSubmit={onBulkSubmit} /></Box>;
  }

  if (action.type === 'SHOW_PAYMENT') {
    return (
      <Box sx={{ mt: 1.5 }}>
        <PaymentCard amount={amount} currency={race?.currency ?? 'BOB'} qrImage={race?.paymentQrImage} onValidated={onPaymentValidated} />
      </Box>
    );
  }

  if (action.type === 'SHOW_REGISTRATION_REVIEW' && registrationReview) {
    return (
      <Box sx={{ mt: 1.5 }}>
        <RegistrationReviewCard
          review={registrationReview}
          loading={confirmationLoading}
          onConfirm={onRegistrationConfirm}
        />
      </Box>
    );
  }

  if (action.type === 'SHOW_THANK_YOU') {
    return <Box sx={{ mt: 1.5 }}><ThankYouCard onHome={onHome} onRestart={onRestart} /></Box>;
  }

  if (action.type === 'SHOW_EXISTING_USER_NEXT_ACTION') {
    return (
      <Box sx={{ mt: 1.5 }}>
        <Button variant="outlined" disabled>
          Continuar con inscripción
        </Button>
      </Box>
    );
  }

  return null;
}
