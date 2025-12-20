// src/types/moderation.type.ts

export interface ModerationTopStats {
  total_user: number;
  total_active_user: number;
  total_post: number;
  total_challenge: number;
}

export interface ModerationUser {
  id: string;
  first_name: string;
  last_name: string;
  role: string;
  is_banned: boolean;
  warning: number;
}

export interface ModerationResponse {
  top: ModerationTopStats;
  users: ModerationUser[];
}

export interface BanUserRequest {
  user_id: string;
}

export interface BanUserResponse {
  msg: string;
  error?: string;
}

export type UnbanUserRequest = BanUserRequest;
export type UnbanUserResponse = BanUserResponse;