import {
  QuestionListResponse,
  QuestionUpdateRequest,
  QuestionUpdateResponse,
} from "@/types/question.type";
import { apiSlice } from "./ApiSlice";

export const questionApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // Get questions for a specific challenge
    getQuestionsByChallenge: builder.query<QuestionListResponse, string>({
      query: (challengeId) => `/admin-api/question-list/${challengeId}/`,
      providesTags: ["Question"],
    }),

    // Update question
    updateQuestion: builder.mutation<
      QuestionUpdateResponse,
      { id: string; body: QuestionUpdateRequest }
    >({
      query: ({ id, body }) => ({
        url: `/admin-api/question-update/${id}/`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Question"],
    }),

    // Delete question
    deleteQuestion: builder.mutation<void, string>({
      query: (id) => ({
        url: `/admin-api/question-delete/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Question"],
    }),
  }),
});

export const {
  useGetQuestionsByChallengeQuery,
  useUpdateQuestionMutation,
  useDeleteQuestionMutation,
} = questionApiSlice;
