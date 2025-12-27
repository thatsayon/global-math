export interface ProfileResponse {
  first_name: string;
  last_name: string;
  profile_pic: string | null;
}

export interface UpdateProfileRequest {
  first_name?: string;
  last_name?: string;
  profile_pic?: File | null;
}

export interface UpdateProfileResponse {
  first_name: string;
  last_name: string;
  profile_pic: string | null;
  access_token: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  detail: string;
}

// Level Adjustment Types
export interface MathLevel {
  id: string;
  name: string;
  slug: string;
}

export interface MathLevelsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: MathLevel[];
}

export interface CreateLevelRequest {
  name: string;
}

export interface CreateLevelResponse {
  id: string;
  name: string;
  slug: string;
}

export type UpdateLevelRequest = CreateLevelRequest;
export type UpdateLevelResponse = CreateLevelResponse;