// src/types/support.type.ts

export interface SupportConversation {
  id: string;
  user_name: string;
  user_role: "student" | "teacher";
  is_closed: boolean;
  created_at: string;
  last_message: string;
  last_message_time: string;
}

export interface SupportConversationListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: SupportConversation[];
}

export interface SupportMessage {
  id: string;
  sender_name: string;
  sender_role: string;
  message: string;
  created_at: string;
}

export interface SupportMessagesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: SupportMessage[];
}

export interface SupportReplyRequest {
  message: string;
}

export interface SupportReplyResponse {
  message: string;
}