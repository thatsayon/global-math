export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  is_banned: boolean;
  date_joined: string;
}

export interface UsersResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: User[];
}

export interface UserRequest {
  page?: number;
  search?: string;
  role?: "student" | "teacher";
  is_banned?: boolean;
}
