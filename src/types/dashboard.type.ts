export interface RecentActivity {
  id: string;
  title: "New user registered" | "New challenge created" | "New classroom created";
  message: string;
  affector_name: string;
  user_type: "student" | "teacher";
  created_at: string;
}

export interface DashboardOverviewResponse {
  total_user: number;
  total_student: number;
  total_teacher: number;
  total_active_user: number;
  total_banned_user: number;
  recent_activities: RecentActivity[];
}