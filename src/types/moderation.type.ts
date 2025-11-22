export interface ModerationTopStats {
  total_user: number;
  total_active_user: number;
  total_post: number;
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
