import { LeaderboardResponse } from "@/types/leaderboard.type";
import { apiSlice } from "./ApiSlice";

export const leaderboardApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getLeaderboard: builder.query<LeaderboardResponse, void>({
      query: () => "/admin-api/leaderboard/",
      providesTags: ["Leaderboard"],
    }),
  }),
});

export const { useGetLeaderboardQuery } = leaderboardApiSlice;