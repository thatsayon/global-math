
import {
  Subject,
  QuestionGenerationRequest,
  QuestionGenerationResponse,
  CreateChallengeRequest,
  CreateChallengeResponse,
} from "@/types/challenge.type"
import { apiSlice } from "./ApiSlice"

export const challengeApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // Get all subjects/levels
    getSubjects: builder.query<Subject[], void>({
      query: () => ({
        url: "/auth/levels/",
        method: "GET",
      }),
      transformResponse: (response: Subject[]) => response,
      providesTags: ["Level"],
    }),

    // Generate questions
    generateQuestions: builder.mutation<
      QuestionGenerationResponse,
      QuestionGenerationRequest
    >({
      query: (body) => ({
        url: "/admin-api/question-generation/",
        method: "POST",
        body,
      }),
    }),

    // Create challenge
    createChallenge: builder.mutation<
      CreateChallengeResponse,
      CreateChallengeRequest
    >({
      query: (body) => ({
        url: "/admin-api/create-challenge/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Moderation"],
    }),
  }),
})

export const {
  useGetSubjectsQuery,
  useGenerateQuestionsMutation,
  useCreateChallengeMutation,
} = challengeApi