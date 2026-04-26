import { appConfig } from '@/config/env';
import { tokenService } from '@/features/access/services/tokenService';
import type { AgentChatResponse } from '@/features/agent/types/agentChat.types';

interface AgentChatApiResponse {
  answer: string;
  sources?: Array<{ source_file: string; chunk_id?: string | null }>;
  intent: AgentChatResponse['intent'];
  ui_action?: { type: 'SHOW_SINGLE_REGISTRATION' | 'SHOW_BULK_REGISTRATION' | 'NONE' } | null;
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

/** Calls the protected CicloAI RAG chat endpoint. */
export const agentChatService = {
  async sendMessage(message: string): Promise<AgentChatResponse> {
    const response = await fetch(`${appConfig.apiBaseUrl}/agent/chat`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${requireAccessToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) throw new Error(await readError(response));

    const payload = (await response.json()) as AgentChatApiResponse;
    return {
      answer: payload.answer,
      intent: payload.intent,
      sources: payload.sources?.map((source) => ({ sourceFile: source.source_file, chunkId: source.chunk_id })),
      uiAction: payload.ui_action ? { type: payload.ui_action.type } : null,
    };
  },
};
