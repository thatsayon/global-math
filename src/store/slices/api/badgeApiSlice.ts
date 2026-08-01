import { apiSlice } from "./ApiSlice";
import {
  AdminBadgesResponse,
  AwardLeaderboardResponse,
} from "@/types/badge.type";

export const badgeApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // GET /admin-api/badges/ — All badges with stats (admin)
    getAdminBadges: builder.query<AdminBadgesResponse, void>({
      query: () => "/admin-api/badges/",
      providesTags: ["Badge"],
    }),

    // POST /admin-api/badges/award-leaderboard/ — Award leaderboard badges
    awardLeaderboardBadges: builder.mutation<AwardLeaderboardResponse, void>({
      query: () => ({
        url: "/admin-api/badges/award-leaderboard/",
        method: "POST",
      }),
      invalidatesTags: ["Badge"],
    }),
  }),
  overrideExisting: false,
});

export const {
  useGetAdminBadgesQuery,
  useAwardLeaderboardBadgesMutation,
} = badgeApiSlice;
