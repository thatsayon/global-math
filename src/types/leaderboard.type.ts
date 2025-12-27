export interface LeaderboardUser {
  rank: number;
  user_id: string;
  username: string;
  profile_pic: string | null;
  level: number;
  total_points: number;
  status: string;
}

export interface LeaderboardResponse {
  count: number;
  results: LeaderboardUser[];
}