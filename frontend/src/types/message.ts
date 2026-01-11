export type RoleType = 'user' | 'assistant' | 'system';

export interface MessageItem {
  id: number;
  role: RoleType;
  content: string;
  created_at: string;
}

export interface MessageListRequest {
  conversation_id: number;
  limit?: number;
}

export interface MessageListResponse {
  conversation_id: number;
  total: number;
  messages: MessageItem[];
}
