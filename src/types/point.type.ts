export interface PointAdjustment {
  id: string;
  classroom_point: number;
  upvote_point: number;
  daily_challenge_point: number;
}

export interface PointAdjustmentUpdateRequest {
  classroom_point: number;
  upvote_point: number;
  daily_challenge_point: number;
}

export type PointAdjustmentUpdateResponse = PointAdjustment;