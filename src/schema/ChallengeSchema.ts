import { z } from "zod"

export const ChallengeSchema = z.object({
  challengeName: z
    .string()
    .min(2, "Challenge name must be at least 2 characters"),

  description: z
    .string()
    .min(5, "Description must be at least 5 characters"),

  difficultyLevel: z
    .number()
    .min(1)
    .max(10, "Difficulty level must be between 1-10"),

  subject: z
    .string()
    .min(1, "Please select a subject"),

  numberOfQuestions: z
    .number()
    .min(1, "Must generate at least 1 question"),

  adjustPoint: z
    .number()
    .min(0, "Points must be 0 or greater"),

  publishDate: z
    .date()
    .refine((date) => date instanceof Date, {
      message: "Please select a publish date",
    }),
})

export type ChallengeFormData = z.infer<typeof ChallengeSchema>
