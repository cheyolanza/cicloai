import type { Race } from '@/features/race/types/race';
import type { RegistrationType } from '@/features/agent/types/registration';

export type AgentState =
  | 'LOADING_RACE'
  | 'EMPTY_RACE'
  | 'RACE_SELECTION'
  | 'AGENT_CHAT'
  | 'NEW_USER_FORM'
  | 'EXISTING_USER_SEARCH'
  | 'EXISTING_USER_REVIEW_COMPLETED'
  | 'BULK_REGISTRATION'
  | 'PAYMENT'
  | 'REGISTRATION_REVIEW'
  | 'THANK_YOU';

export type AgentUiAction =
  | { type: 'SHOW_OPTIONS'; options: Array<{ label: string; value: RegistrationType }> }
  | { type: 'SHOW_FORM'; form: 'NEW_USER_REGISTRATION' | 'EXISTING_USER_SEARCH' | 'BULK_REGISTRATION' }
  | { type: 'SHOW_EXISTING_USER_NEXT_ACTION' }
  | { type: 'SHOW_PAYMENT' }
  | { type: 'SHOW_REGISTRATION_REVIEW' }
  | { type: 'SHOW_THANK_YOU' }
  | { type: 'SHOW_EMPTY_RACE_MESSAGE' };

export interface ChatMessage {
  id: string;
  role: 'agent' | 'user';
  text: string;
  createdAt: string;
  uiAction?: AgentUiAction;
  race?: Race;
}

export interface AgentServiceResponse {
  reply: string;
  state: AgentState;
  ui_action?: AgentUiAction;
}
