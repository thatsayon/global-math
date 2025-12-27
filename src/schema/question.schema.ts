import { z } from "zod";

export const questionUpdateSchema = z.object({
  order: z.coerce.number().int().min(1, "Order must be at least 1"),
  question_text: z.string().min(1, "Question text is required"),
  answer: z.string().min(1, "Answer is required"),
});