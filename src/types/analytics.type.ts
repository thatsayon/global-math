export interface Summary {
  total_users: number;
  active_users: number;
  total_challenges: number;
}

export interface UsageAnalytics {
  month: string;
  users: number;
  engagement: number;
  activity: number;
}

export interface EngagementUser {
  no: number;
  id: string;
  name: string;
  role: "student" | "teacher";
  profile_pic: string | null;
  challenges: number;
  engagement_score: number;
  last_active: string | null;
}

export interface StudentEngagement {
  count: number;
  next: string | null;
  previous: string | null;
  results: EngagementUser[];
}

export interface AnalyticsResponse {
  summary: Summary;
  available_years: number[];
  selected_year: number;
  usage_analytics: UsageAnalytics[];
  student_engagement: StudentEngagement;
}