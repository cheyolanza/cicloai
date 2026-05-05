import { Avatar, Box, Button, Paper, Stack, Typography } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import { Link as RouterLink } from 'react-router-dom';
import type { ChatMessage } from '@/features/agent/types/conversation';
import { RichMessageRenderer } from '@/features/agent/components/chat/RichMessageRenderer';
import type {
  BulkRegistrationSummary,
  NewUserRegistration,
  RegistrationType,
} from '@/features/agent/types/registration';
import type { Race } from '@/features/race/types/race';
import type { FirstRaceRegistrationReview } from '@/features/registration/types/registrationReview';
import { isAccessRequiredMessage } from '@/components/common/accessRequired';
import type { BikerLookupActionResult } from '@/features/biker-search/types/bikerSearch.types';

interface ChatMessageBubbleProps {
  amount: number;
  message: ChatMessage;
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
  onPaymentRetry: () => void;
}

/** Single chat bubble with optional rich action content. */
export function ChatMessageBubble({
  amount,
  message,
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
  onPaymentRetry,
}: ChatMessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <Stack direction="row" spacing={1.25} justifyContent={isUser ? 'flex-end' : 'flex-start'}>
      {!isUser ? <Avatar sx={{ bgcolor: 'primary.main' }}><SmartToyIcon /></Avatar> : null}
      <Box sx={{ maxWidth: { xs: '92%', md: '76%' } }}>
        <Paper
          elevation={0}
          sx={{
            p: 1.5,
            border: '1px solid',
            borderColor: isUser ? 'primary.main' : 'divider',
            bgcolor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            borderRadius: 2,
          }}
        >
          <Typography>{message.text}</Typography>
          {isAccessRequiredMessage(message.text) ? (
            <Button
              color={isUser ? 'inherit' : 'primary'}
              component={RouterLink}
              size="small"
              sx={{ mt: 1 }}
              to="/"
              variant={isUser ? 'outlined' : 'contained'}
            >
              Volver al inicio
            </Button>
          ) : null}
          {!isUser ? (
            <RichMessageRenderer
              action={message.uiAction}
              amount={amount}
              race={message.race ?? race}
              registrationReview={registrationReview}
              confirmationLoading={confirmationLoading}
              onHome={onHome}
              onRestart={onRestart}
              onOptionSelect={onOptionSelect}
              onBulkSubmit={onBulkSubmit}
              onExistingUserSubmit={onExistingUserSubmit}
              onNewUserSubmit={onNewUserSubmit}
              onPaymentValidated={onPaymentValidated}
              onRegistrationConfirm={onRegistrationConfirm}
              onPaymentRetry={onPaymentRetry}
            />
          ) : null}
        </Paper>
      </Box>
      {isUser ? <Avatar sx={{ bgcolor: 'secondary.main' }}><PersonIcon /></Avatar> : null}
    </Stack>
  );
}
