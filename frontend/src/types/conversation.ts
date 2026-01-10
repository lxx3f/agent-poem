export interface ConversationCreateRequest {
  title?: string;
  agent_id: number;
}

export interface ConversationCreateResponse {
  conversation_id: number;
}

export interface ConversationListRequest {
  agent_id: number;
  limit?: number;
  offset?: number;
}

export interface ConversationItem {
  id: number;
  agent_id: number;
  title?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  conversations: ConversationItem[];
  total: number;
}
