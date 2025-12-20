// src/features/api/moderationApiSlice.ts
import { apiSlice } from "./ApiSlice";
import {
  ModerationResponse,
  BanUserRequest,
  BanUserResponse,
  UnbanUserRequest,
  UnbanUserResponse,
} from "@/types/moderation.type";

export const moderationApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getModerationData: builder.query<
      ModerationResponse,
      { page?: number; filter?: string }
    >({
      query: ({ page = 1, filter = "all" }) => ({
        url: "/admin-api/moderation/",
        params: { page, filter },
      }),
      providesTags:["Moderation"]
    }),

    banUser: builder.mutation<BanUserResponse, BanUserRequest>({
      query: (body) => ({
        url: "/admin-api/ban/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Moderation"]
    }),

    unbanUser: builder.mutation<UnbanUserResponse, UnbanUserRequest>({
      query: (body) => ({
        url: "/admin-api/unban/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Moderation"]
    }),
  }),
});

export const {
  useGetModerationDataQuery,
  useBanUserMutation,
  useUnbanUserMutation,
} = moderationApiSlice;