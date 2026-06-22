// src/features/api/moderationApiSlice.ts
import { apiSlice } from "./ApiSlice";
import {
  ModerationResponse,
  BanUserRequest,
  BanUserResponse,
  UnbanUserRequest,
  UnbanUserResponse,
  AdminPostsResponse,
  AdminCommentsResponse,
} from "@/types/moderation.type";

export const moderationApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getModerationData: builder.query<
      ModerationResponse,
      { page?: number; filter?: string }
    >({
      query: ({ page = 1, filter = "all" }) => {
        const params: Record<string, any> = { page };
        if (filter === "student") params.role = "student";
        if (filter === "teacher") params.role = "teacher";
        if (filter === "banned") params.is_banned = "true";
        return {
          url: "/admin-api/moderation/",
          params,
        };
      },
      providesTags: ["Moderation"],
    }),

    banUser: builder.mutation<BanUserResponse, BanUserRequest>({
      query: (body) => ({
        url: "/admin-api/ban/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Moderation"],
    }),

    unbanUser: builder.mutation<UnbanUserResponse, UnbanUserRequest>({
      query: (body) => ({
        url: "/admin-api/unban/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Moderation"],
    }),

    getAdminPosts: builder.query<AdminPostsResponse, { page?: number; search?: string }>({
      query: ({ page = 1, search = "" }) => ({
        url: "/admin-api/admin-posts/",
        params: { page, ...(search ? { search } : {}) },
      }),
      providesTags: ["Moderation"],
    }),

    deleteAdminPost: builder.mutation<void, string>({
      query: (id) => ({
        url: `/admin-api/admin-posts/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Moderation"],
    }),

    getAdminComments: builder.query<AdminCommentsResponse, { page?: number; search?: string }>({
      query: ({ page = 1, search = "" }) => ({
        url: "/admin-api/admin-comments/",
        params: { page, ...(search ? { search } : {}) },
      }),
      providesTags: ["Moderation"],
    }),

    deleteAdminComment: builder.mutation<void, string>({
      query: (id) => ({
        url: `/admin-api/admin-comments/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Moderation"],
    }),
  }),
  overrideExisting: false,
});

export const {
  useGetModerationDataQuery,
  useBanUserMutation,
  useUnbanUserMutation,
  useGetAdminPostsQuery,
  useDeleteAdminPostMutation,
  useGetAdminCommentsQuery,
  useDeleteAdminCommentMutation,
} = moderationApiSlice;