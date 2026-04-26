import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material';
import { BrandMark } from '@/components/common/BrandMark';
import { FullScreenFlowLayout } from '@/components/layout/FullScreenFlowLayout';
import { ChatMessageList } from '@/features/agent/components/chat/ChatMessageList';
import { useAgentConversation } from '@/features/agent/hooks/useAgentConversation';
import { AccessRequiredAlert } from '@/components/common/AccessRequiredAlert';
import { isAccessRequiredMessage } from '@/components/common/accessRequired';
import { AgentChatInput } from '@/features/agent/components/AgentChatInput';
import { AgentConversationPanel } from '@/features/agent/components/AgentConversationPanel';

/**
 * Conversational agent surface for CicloAI.
 * The visible experience is chat-first while `useAgentConversation` keeps the
 * deterministic state machine hidden behind agent messages and UI actions.
 */
export function AgentChatPage() {
  const conversation = useAgentConversation();

  return (
    <FullScreenFlowLayout maxWidth="lg">
      <Stack sx={{ height: '100%', py: { xs: 0.5, md: 1 } }} spacing={1.5}>
        <BrandMark />
        <AgentConversationPanel
          input={
            <AgentChatInput
              disabled={!conversation.chatInputEnabled}
              onSend={(message) => void conversation.sendFreeChatMessage(message)}
            />
          }
        >
          {conversation.loading ? (
            <Stack sx={{ flex: 1, alignItems: 'center', justifyContent: 'center' }} spacing={2}>
              <CircularProgress />
              <Typography color="text.secondary">CicloAI está buscando la carrera activa...</Typography>
            </Stack>
          ) : conversation.error ? (
            <Box sx={{ flex: 1, display: 'grid', placeItems: 'center', p: 3 }}>
              {isAccessRequiredMessage(conversation.error) ? (
                <AccessRequiredAlert message={conversation.error} />
              ) : (
                <Alert severity="warning" sx={{ width: '100%', maxWidth: 560 }}>{conversation.error}</Alert>
              )}
            </Box>
          ) : (
            <ChatMessageList
              amount={conversation.amount}
              confirmationLoading={conversation.confirmationLoading}
              isAgentTyping={conversation.isAgentTyping}
              messages={conversation.messages}
              race={conversation.race}
              registrationReview={conversation.registrationReview}
              onHome={conversation.goHome}
              onRestart={() => void conversation.restartConversation()}
              onOptionSelect={(type) => void conversation.chooseRegistrationType(type)}
              onBulkSubmit={(summary) => void conversation.submitBulkRegistration(summary)}
              onExistingUserSubmit={(user) => void conversation.submitExistingUser(user)}
              onNewUserSubmit={(registration) => void conversation.submitNewUser(registration)}
              onPaymentValidated={(proof) => void conversation.validatePayment(proof)}
              onRegistrationConfirm={() => void conversation.confirmRegistration()}
            />
          )}

        </AgentConversationPanel>
      </Stack>
    </FullScreenFlowLayout>
  );
}
