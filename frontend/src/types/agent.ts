export interface AgentItem {
  id: number;
  name: string;
  code: string;
  description: string;
  workflow_key: string;
  system_prompt: string;
  parameters?: string | null;
  llm_config?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentListRequest {
  limit?: number;
}

export interface AgentListResponse {
  total: number;
  agents: AgentItem[];
}

export interface AgentRunRequest {
  user_input: string;
  conversation_id: number;
  workflow?: 'poetry_game' | 'rag_chat';
  history_limit?: number;
}

export interface AgentRunResponse {
  message: string;
}
