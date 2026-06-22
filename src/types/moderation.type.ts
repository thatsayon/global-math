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

export interface PostAuthor {
  id: string;
  first_name: string;
  last_name: string;
  username: string;
  role: string;
}

export interface AdminPost {
  id: string;
  author: PostAuthor | null;
  text: string | null;
  image: string | null;
  video: string | null;
  classroom_name: string | null;
  created_at: string;
  comment_count: number;
  is_verified: boolean;
}

export interface AdminComment {
  id: string;
  author: PostAuthor | null;
  text: string | null;
  image: string | null;
  post_id: string;
  post_text: string | null;
  created_at: string;
}

export interface AdminPostsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminPost[];
}

export interface AdminCommentsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminComment[];
}