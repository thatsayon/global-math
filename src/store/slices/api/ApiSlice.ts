import { Summary } from "@/types/analytics.type";
import { loginRequest, loginResponse } from "@/types/auth.type";
import { UserRequest, UsersResponse } from "@/types/user.type";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from "@reduxjs/toolkit/query/react";
import { getCookie, setCookie, removeCookie } from "@/hooks/cookie";

const baseQuery = fetchBaseQuery({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "https://api.mathos.cloud",
  prepareHeaders: (headers) => {
    if (typeof window !== "undefined") {
      const accessToken = getCookie("access");

      if (accessToken) {
        headers.set("Authorization", `Bearer ${accessToken}`);
      }
    }
    return headers;
  },
});

let refreshPromise: Promise<any> | null = null;

const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  if (result.error && result.error.status === 401) {
    if (typeof window !== "undefined") {
      const refreshToken = getCookie("refresh");

      if (refreshToken) {
        if (!refreshPromise) {
          refreshPromise = fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.mathos.cloud"}/auth/generate-access-token/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken }),
          }).then(async (res) => {
            if (!res.ok) throw new Error("Refresh failed");
            return res.json();
          });
        }

        try {
          const { access } = await refreshPromise;
          setCookie("access", access, 5 / 1440);
          result = await baseQuery(args, api, extraOptions);
        } catch (err) {
          removeCookie("access");
          removeCookie("refresh");
          window.location.href = "/";
        } finally {
          refreshPromise = null;
        }
      } else {
        removeCookie("access");
        removeCookie("refresh");
        window.location.href = "/";
      }
    }
  }
  return result;
};

export const apiSlice = createApi({
  reducerPath: "api",
  baseQuery: baseQueryWithReauth,
  tagTypes: ["User", "Profile", "Level", "Moderation", "Challenge", "Question", "PointAdjustment","Analytics", "Conversation", "Leaderboard", "Badge"],

  endpoints: (builder) => ({
    // auth endpoints _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

    login: builder.mutation<loginResponse, loginRequest>({
      query: (body) => ({
        url: "/auth/login/",
        method: "POST",
        body,
      }),
    }),

    // user endpoints _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

    getUsers: builder.query<UsersResponse, UserRequest>({
      query: ({ page = 1, search = "", role = "all", is_banned = "all" }) => ({
        url: "/admin-api/user-management/",
        params: {
          page,
          ...(search ? { search } : {}),
          ...(role !== "all" ? { role } : {}),
          ...(is_banned !== "all" ? { is_banned } : {}),
        },
        method: "GET",
      }),
      providesTags: ["User"]
    }),
    getTopCardInfo: builder.query<Summary, void>({
      query: ()=> "/admin-api/top/"
    })
  }),
});

export const {
  // auth endpoints
  useLoginMutation,
  // user endpoints
  useGetUsersQuery,
  useGetTopCardInfoQuery
} = apiSlice;
