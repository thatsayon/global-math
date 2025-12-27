import { AnalyticsResponse } from "@/types/analytics.type";
import { apiSlice } from "./ApiSlice";

export const analyticsApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getAnalytics: builder.query<
      AnalyticsResponse,
      { page?: number; year?: number }
    >({
      query: ({ page = 1, year }) => ({
        url: "/admin-api/analytics/",
        params: {
          page,
          ...(year ? { year } : {}),
        },
      }),
      providesTags: ["Analytics"],
    }),
  }),
});

export const { useGetAnalyticsQuery } = analyticsApiSlice;