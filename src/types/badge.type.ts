export type BadgeCategory =
  | "Streak"
  | "Engagement"
  | "Academic"
  | "Social"
  | "Challenge"
  | "Special";

export interface Badge {
  code: string;
  name: string;
  description: string;
  icon: string;
  category: BadgeCategory;
  earner_count: number;
  recent_earners: RecentEarner[];
}

export interface RecentEarner {
  name: string;
  earned_at: string;
}

export interface AdminBadgesResponse {
  total_badges: number;
  total_earned: number;
  badges: Badge[];
}

export interface StudentBadgeWithStatus {
  code: string;
  name: string;
  description: string;
  icon: string;
  category: BadgeCategory;
  earned: boolean;
  earned_at: string | null;
}

export interface AwardLeaderboardResponse {
  message: string;
  newly_awarded: { rank: number; badge: string }[];
}
