import {
  Subject,
  QuestionGenerationRequest,
  QuestionGenerationResponse,
  CreateChallengeRequest,
  CreateChallengeResponse,
  ChallengeUpdateResponse,
  ChallengeUpdateRequest,
  ChallengeListResponse,
} from "@/types/challenge.type";
import { apiSlice } from "./ApiSlice";

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

    getDailyChallenges: builder.query<
      ChallengeListResponse,
      { page?: number; subject?: string }
    >({
      query: ({ page = 1, subject = "" }) => ({
        url: "/admin-api/challenge-list/",
        params: {
          page,
          ...(subject ? { subject } : {}),
        },
      }),
      providesTags: ["Challenge"],
    }),

    // NEW: Update daily challenge
    updateDailyChallenge: builder.mutation<
      ChallengeUpdateResponse,
      { id: string; body: ChallengeUpdateRequest }
    >({
      query: ({ id, body }) => ({
        url: `/admin-api/challenge-update/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Challenge"],
    }),

    // NEW: Delete daily challenge
    deleteDailyChallenge: builder.mutation<void, string>({
      query: (id) => ({
        url: `/admin-api/challenge-delete/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Challenge"],
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
      invalidatesTags: ["Challenge"],
    }),
  }),
});

export const {
  useGetSubjectsQuery,
  useGenerateQuestionsMutation,
  useCreateChallengeMutation,
  useGetDailyChallengesQuery,
  useUpdateDailyChallengeMutation,
  useDeleteDailyChallengeMutation,
} = challengeApi;
