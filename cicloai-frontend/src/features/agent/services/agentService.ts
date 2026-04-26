import type { AgentServiceResponse } from '@/features/agent/types/conversation';
import type { Race } from '@/features/race/types/race';
import type { RegistrationType } from '@/features/agent/types/registration';

/**
 * Mock agent adapter. The UI already consumes a backend-friendly contract
 * (`reply`, `state`, `ui_action`), so a future FastAPI agent endpoint can
 * replace these deterministic responses without changing chat components.
 */
export const agentService = {
  async introduceRace(race: Race | null): Promise<AgentServiceResponse> {
    await new Promise((resolve) => window.setTimeout(resolve, 250));

    if (!race) {
      return {
        reply: 'No hay carreras habilitadas actualmente. Te avisaremos cuando exista una nueva convocatoria.',
        state: 'EMPTY_RACE',
        ui_action: { type: 'SHOW_EMPTY_RACE_MESSAGE' },
      };
    }

    return {
      reply: `Hola, soy CicloAI. Encontré una carrera activa: ${race.name}. ¿Qué tipo de inscripción deseas realizar?`,
      state: 'RACE_SELECTION',
      ui_action: {
        type: 'SHOW_OPTIONS',
        options: [
          { label: 'Inscripción unitaria', value: 'new' },
          { label: 'Inscripción masiva', value: 'bulk' },
          { label: 'Charlar con el Agente', value: 'chat' },
        ],
      },
    };
  },

  async chooseRegistrationType(type: RegistrationType): Promise<AgentServiceResponse> {
    await new Promise((resolve) => window.setTimeout(resolve, 250));

    if (type === 'new') {
      return {
        reply: 'Perfecto, vamos a registrar tu primera carrera. Necesito tus datos básicos.',
        state: 'NEW_USER_FORM',
        ui_action: { type: 'SHOW_FORM', form: 'NEW_USER_REGISTRATION' },
      };
    }

    if (type === 'chat') {
      return {
        reply: 'Listo, puedes preguntarme sobre la convocatoria de la carrera.',
        state: 'AGENT_CHAT',
      };
    }

    return {
      reply: 'Vamos con una inscripción masiva. Sube la planilla para calcular el total de competidores.',
      state: 'BULK_REGISTRATION',
      ui_action: { type: 'SHOW_FORM', form: 'BULK_REGISTRATION' },
    };
  },

  async requestPayment(): Promise<AgentServiceResponse> {
    await new Promise((resolve) => window.setTimeout(resolve, 250));
    return {
      reply: 'Ya tengo la información necesaria. Te muestro el monto y el QR para realizar el pago.',
      state: 'PAYMENT',
      ui_action: { type: 'SHOW_PAYMENT' },
    };
  },

  async finishRegistration(): Promise<AgentServiceResponse> {
    await new Promise((resolve) => window.setTimeout(resolve, 250));
    return {
      reply: 'Gracias por completar tu inscripción.',
      state: 'THANK_YOU',
      ui_action: { type: 'SHOW_THANK_YOU' },
    };
  },
};
