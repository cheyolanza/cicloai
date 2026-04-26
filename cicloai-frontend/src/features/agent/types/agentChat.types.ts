export type AgentChatIntent = 'rag_answer' | 'start_single_registration' | 'start_bulk_registration';

export interface AgentChatRequest {
  message: string;
}

export interface AgentChatSource {
  sourceFile: string;
  chunkId?: string | null;
}

export interface AgentChatUiAction {
  type: 'SHOW_SINGLE_REGISTRATION' | 'SHOW_BULK_REGISTRATION' | 'NONE';
}

export interface AgentChatResponse {
  answer: string;
  sources?: AgentChatSource[];
  intent: AgentChatIntent;
  uiAction?: AgentChatUiAction | null;
}
