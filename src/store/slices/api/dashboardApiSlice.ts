import { apiSlice } from "./ApiSlice";
import { DashboardOverviewResponse } from "@/types/dashboard.type";

export const dashboardApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getDashboardOverview: builder.query<DashboardOverviewResponse, void>({
      query: () => ({
        url: "/admin-api/overview/",
        method: "GET",
      }),
    }),
  }),
});

export const { useGetDashboardOverviewQuery } = dashboardApiSlice;