import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAccessSession } from '@/features/access/context/AccessSessionContext';
import { agentService } from '@/features/agent/services/agentService';
import { agentChatService } from '@/features/agent/services/agentChatService';
import type { AgentState, ChatMessage } from '@/features/agent/types/conversation';
import type {
  BulkRegistrationSummary,
  NewUserRegistration,
  RegistrationType,
} from '@/features/agent/types/registration';
import { raceService } from '@/features/race/services/raceService';
import type { Race } from '@/features/race/types/race';
import { paymentService } from '@/features/payment/services/paymentService';
import { registrationService } from '@/features/registration/services/registrationService';
import type { FirstRaceRegistrationReview } from '@/features/registration/types/registrationReview';
import type { BikerLookupActionResult } from '@/features/biker-search/types/bikerSearch.types';

function messageId(): string {
  return crypto.randomUUID();
}

function now(): string {
  return new Date().toISOString();
}

/**
 * Conversation state machine for the CicloAI agent.
 * UI components render chat messages only; this hook owns deterministic flow
 * transitions until a real FastAPI agent session endpoint takes over.
 */
export function useAgentConversation() {
  const navigate = useNavigate();
  const { hasTemporaryToken, clearTemporarySession } = useAccessSession();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [race, setRace] = useState<Race | null>(null);
  const [state, setState] = useState<AgentState>('LOADING_RACE');
  const [registrationType, setRegistrationType] = useState<RegistrationType | null>(null);
  const [newUserRegistration, setNewUserRegistration] = useState<NewUserRegistration | null>(null);
  const [registrationReview, setRegistrationReview] = useState<FirstRaceRegistrationReview | null>(null);
  const [bulkSummary, setBulkSummary] = useState<BulkRegistrationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirmationLoading, setConfirmationLoading] = useState(false);
  const [pendingAgentResponses, setPendingAgentResponses] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const competitorsCount = registrationType === 'bulk' ? bulkSummary?.competitorsDetected ?? 0 : 1;
  const amount = useMemo(() => {
    if (!race || !registrationType) return 0;
    if (registrationType === 'bulk' && bulkSummary?.totalAmount) return bulkSummary.totalAmount;
    return paymentService.calculateAmount({
      registrationType,
      competitorsCount,
      unitPrice: race.inscriptionPrice,
    });
  }, [competitorsCount, race, registrationType]);

  const appendAgentMessage = useCallback((message: Omit<ChatMessage, 'id' | 'role' | 'createdAt'>): void => {
    setMessages((current) => [...current, { ...message, id: messageId(), role: 'agent', createdAt: now() }]);
  }, []);

  const appendUserMessage = useCallback((text: string): void => {
    setMessages((current) => [...current, { id: messageId(), role: 'user', text, createdAt: now() }]);
  }, []);

  const resetConversationState = useCallback((): void => {
    setMessages([]);
    setRegistrationType(null);
    setNewUserRegistration(null);
    setRegistrationReview(null);
    setBulkSummary(null);
    setConfirmationLoading(false);
    setError(null);
    setPendingAgentResponses(0);
    setState('RACE_SELECTION');
  }, []);

  const loadWelcomeConversation = useCallback(async (currentRace: Race | null): Promise<void> => {
    if (!currentRace) return;

    const response = await agentService.introduceRace(currentRace);
    setState(response.state);
    appendAgentMessage({
      text: response.reply,
      uiAction: response.ui_action,
      race: currentRace ?? undefined,
    });
  }, [appendAgentMessage]);

  async function runWithAgentTyping(task: () => Promise<void>): Promise<void> {
    setPendingAgentResponses((current) => current + 1);
    try {
      await task();
    } finally {
      setPendingAgentResponses((current) => Math.max(0, current - 1));
    }
  }

  useEffect(() => {
    if (!hasTemporaryToken) {
      navigate('/', { replace: true });
      return;
    }

    raceService
      .getEnabledRace()
      .then(async (enabledRace) => {
        setRace(enabledRace);
        await loadWelcomeConversation(enabledRace);
      })
      .catch((currentError) => {
        setError(currentError instanceof Error ? currentError.message : 'No pudimos iniciar el agente.');
      })
      .finally(() => setLoading(false));
  }, [appendAgentMessage, hasTemporaryToken, loadWelcomeConversation, navigate]);

  async function chooseRegistrationType(type: RegistrationType): Promise<void> {
    const labels: Record<RegistrationType, string> = {
      new: 'Inscripción unitaria',
      existing: 'Buscar mis datos',
      bulk: 'Inscripción masiva',
      chat: 'Charlar con el Agente',
    };
    appendUserMessage(labels[type]);
    setRegistrationType(type);
    await runWithAgentTyping(async () => {
      const response = await agentService.chooseRegistrationType(type);
      setState(response.state);
      appendAgentMessage({ text: response.reply, uiAction: response.ui_action });
    });
  }

  async function sendFreeChatMessage(message: string): Promise<void> {
    appendUserMessage(message);

    await runWithAgentTyping(async () => {
      try {
        const response = await agentChatService.sendMessage(message);
        if (response.intent === 'start_single_registration') {
          setRegistrationType('new');
          setState('NEW_USER_FORM');
          appendAgentMessage({
            text: response.answer,
            uiAction: { type: 'SHOW_FORM', form: 'NEW_USER_REGISTRATION' },
          });
          return;
        }

        if (response.intent === 'start_bulk_registration') {
          setRegistrationType('bulk');
          setState('BULK_REGISTRATION');
          appendAgentMessage({
            text: response.answer,
            uiAction: { type: 'SHOW_FORM', form: 'BULK_REGISTRATION' },
          });
          return;
        }

        setState('AGENT_CHAT');
        appendAgentMessage({ text: response.answer });
      } catch (currentError) {
        appendAgentMessage({
          text: currentError instanceof Error ? currentError.message : 'No pude responder en este momento.',
        });
      }
    });
  }

  async function submitNewUser(registration: NewUserRegistration): Promise<void> {
    setNewUserRegistration(registration);
    appendUserMessage('Ya completé mis datos de inscripción.');
    await runWithAgentTyping(async () => {
      const response = await agentService.requestPayment();
      setState(response.state);
      appendAgentMessage({ text: response.reply, uiAction: response.ui_action });
    });
  }

  async function submitExistingUser(result: BikerLookupActionResult): Promise<void> {
    appendUserMessage('Confirmé la actualización del equipo.');
    setState('EXISTING_USER_REVIEW_COMPLETED');
    appendAgentMessage({
      text: `${result.message} Este flujo no inscribe automáticamente al ciclista en la carrera activa.`,
      uiAction: { type: 'SHOW_EXISTING_USER_NEXT_ACTION' },
    });
  }

  async function submitBulkRegistration(summary: BulkRegistrationSummary): Promise<void> {
    setBulkSummary(summary);
    appendUserMessage(`Subí la planilla con ${summary.competitorsDetected} competidores.`);
    await runWithAgentTyping(async () => {
      const response = await agentService.requestPayment();
      setState(response.state);
      appendAgentMessage({
        text: `${summary.message ?? response.reply} Monto total esperado: ${summary.totalAmount ?? amount} ${summary.currency ?? race?.currency ?? 'BOB'}.`,
        uiAction: response.ui_action,
      });
    });
  }

  async function validatePayment(proof: File): Promise<void> {
    appendUserMessage('Ya subí mi comprobante de pago.');

    await runWithAgentTyping(async () => {
      if (registrationType === 'bulk') {
        const response = await agentService.finishRegistration();
        setState(response.state);
        appendAgentMessage({
          text: `Pago recibido para inscripción masiva. ${response.reply}`,
          uiAction: response.ui_action,
        });
        return;
      }

      if (!newUserRegistration) {
        setError('No encontramos los datos del ciclista para revisar la inscripción.');
        return;
      }

      try {
        const review = await registrationService.reviewFirstRaceRegistration(newUserRegistration, proof);
        setRegistrationReview(review);
        setState(review.paymentStatus === 'validated' ? 'REGISTRATION_REVIEW' : 'PAYMENT');
        appendAgentMessage({
          text: review.paymentStatus === 'validated'
            ? 'Revisé tus datos, el comprobante y la categoría. Confirma el resumen para registrar tu inscripción.'
            : 'Revisé tus datos y la categoría, pero el comprobante no pasó la validación de pago.',
          uiAction: { type: 'SHOW_REGISTRATION_REVIEW' },
        });
      } catch (currentError) {
        appendAgentMessage({
          text: currentError instanceof Error ? currentError.message : 'No pude revisar la inscripción. Intenta nuevamente.',
        });
      }
    });
  }

  async function confirmRegistration(): Promise<void> {
    if (!registrationReview) return;

    setConfirmationLoading(true);
    appendUserMessage('Confirmo que los datos son correctos.');

    await runWithAgentTyping(async () => {
      try {
        const result = await registrationService.confirmFirstRaceRegistration(registrationReview.reviewToken);
        setState('THANK_YOU');
        appendAgentMessage({ text: result.message, uiAction: { type: 'SHOW_THANK_YOU' } });
      } catch (currentError) {
        appendAgentMessage({
          text: currentError instanceof Error ? currentError.message : 'No pude registrar la inscripción.',
        });
      } finally {
        setConfirmationLoading(false);
      }
    });
  }

  function goHome(): void {
    clearTemporarySession();
    navigate('/', { replace: true });
  }

  async function restartConversation(): Promise<void> {
    resetConversationState();
    await loadWelcomeConversation(race);
  }

  return {
    amount,
    confirmationLoading,
    error,
    goHome,
    loading,
    messages,
    isAgentTyping: pendingAgentResponses > 0,
    race,
    registrationReview,
    state,
    chatInputEnabled: state === 'AGENT_CHAT',
    confirmRegistration,
    chooseRegistrationType,
    sendFreeChatMessage,
    restartConversation,
    submitBulkRegistration,
    submitExistingUser,
    submitNewUser,
    validatePayment,
  };
}
