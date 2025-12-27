import { z } from "zod";

export const pointAdjustmentSchema = z.object({
  classroomPoint: z.coerce.number().min(0, "Classroom point must be 0 or greater"),
  upvotePoint: z.coerce.number().min(0, "Upvote point must be 0 or greater"),
  dailyChallengePoint: z.coerce.number().min(0, "Daily challenge point must be 0 or greater"),
});