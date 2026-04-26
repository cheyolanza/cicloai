import { useEffect, useMemo, useRef } from 'react';
import { Avatar, Box, Paper, Stack, Typography } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import type { ChatMessage } from '@/features/agent/types/conversation';
import { ChatMessageBubble } from '@/features/agent/components/chat/ChatMessageBubble';
import type {
  BulkRegistrationSummary,
  NewUserRegistration,
  RegistrationType,
} from '@/features/agent/types/registration';
import type { Race } from '@/features/race/types/race';
import type { FirstRaceRegistrationReview } from '@/features/registration/types/registrationReview';
import type { BikerLookupActionResult } from '@/features/biker-search/types/bikerSearch.types';

interface ChatMessageListProps {
  amount: number;
  messages: ChatMessage[];
  race: Race | null;
  registrationReview: FirstRaceRegistrationReview | null;
  confirmationLoading: boolean;
  isAgentTyping: boolean;
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
 * Scrollable message timeline.
 * The chat owns its own scroll position and follows the agent's newest rich
 * content, including cards that grow after render, while page scroll remains
 * disabled outside this area.
 */
export function ChatMessageList(props: ChatMessageListProps) {
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const messageStackRef = useRef<HTMLDivElement | null>(null);
  const endOfMessagesRef = useRef<HTMLDivElement | null>(null);

  const scrollSignal = useMemo(() => {
    const lastMessage = props.messages.at(-1);
    return [
      props.messages.length,
      lastMessage?.id ?? '',
      lastMessage?.uiAction?.type ?? '',
	      props.registrationReview?.reviewToken ?? '',
	      props.confirmationLoading ? 'confirming' : 'idle',
	      props.isAgentTyping ? 'typing' : 'idle',
	    ].join(':');
	  }, [props.confirmationLoading, props.isAgentTyping, props.messages, props.registrationReview?.reviewToken]);

  function scrollToLatestMessage(behavior: ScrollBehavior = 'smooth'): void {
    window.requestAnimationFrame(() => {
      endOfMessagesRef.current?.scrollIntoView({ behavior, block: 'end' });
    });
  }

  useEffect(() => {
    scrollToLatestMessage();
  }, [scrollSignal]);

  useEffect(() => {
    const messageStack = messageStackRef.current;
    if (!messageStack || typeof ResizeObserver === 'undefined') return undefined;

    const observer = new ResizeObserver(() => {
      scrollToLatestMessage('auto');
    });
    observer.observe(messageStack);

    return () => observer.disconnect();
  }, []);

	return (
	    <Box ref={scrollContainerRef} sx={{ flex: 1, overflowY: 'auto', px: { xs: 1.5, md: 3 }, py: 2 }}>
	      <Stack ref={messageStackRef} spacing={2}>
	        {props.messages.map((message) => (
	          <ChatMessageBubble key={message.id} {...props} message={message} />
	        ))}
	        {props.isAgentTyping ? <AgentTypingIndicator /> : null}
	        <Box ref={endOfMessagesRef} aria-hidden="true" sx={{ height: 1 }} />
	      </Stack>
	    </Box>
	  );
	}

function AgentTypingIndicator() {
  return (
    <Stack direction="row" spacing={1.25} justifyContent="flex-start">
      <Avatar sx={{ bgcolor: 'primary.main' }}>
        <SmartToyIcon />
      </Avatar>
      <Box sx={{ maxWidth: { xs: '92%', md: '76%' } }}>
        <Paper
          elevation={0}
          sx={{
            p: 1.5,
            border: '1px solid',
            borderColor: 'primary.main',
            bgcolor: 'rgba(15, 118, 110, 0.08)',
            color: 'primary.dark',
            borderRadius: 2,
          }}
        >
          <Stack direction="row" spacing={1.25} alignItems="center">
            <Typography fontWeight={700}>CicloAI está escribiendo</Typography>
            <Stack direction="row" spacing={0.5} aria-hidden="true">
              {[0, 1, 2].map((index) => (
                <Box
                  key={index}
                  sx={{
                    width: 7,
                    height: 7,
                    borderRadius: '50%',
                    bgcolor: 'primary.main',
                    animation: 'cicloaiTyping 1s ease-in-out infinite',
                    animationDelay: `${index * 0.16}s`,
                    '@keyframes cicloaiTyping': {
                      '0%, 80%, 100%': { opacity: 0.35, transform: 'translateY(0)' },
                      '40%': { opacity: 1, transform: 'translateY(-4px)' },
                    },
                  }}
                />
              ))}
            </Stack>
          </Stack>
        </Paper>
      </Box>
    </Stack>
  );
}
