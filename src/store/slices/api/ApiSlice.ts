// src/features/api/ApiSlice.ts
import { RootState } from "@/store/store";
import { loginRequest, loginResponse } from "@/types/auth.type";
import { UserRequest, UsersResponse } from "@/types/user.type";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const apiSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "https://api.mathos.cloud",
    prepareHeaders: (headers) => {
      headers.set("Content-Type", "application/json");

      if (typeof window !== "undefined") {
        const accessToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access="))
          ?.split("=")[1];

        if (accessToken) {
          headers.set("Authorization", `Bearer ${accessToken}`);
        }
      }
      return headers;
    },
  }),
  tagTypes: ["User"],
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
      query: ({ page = 1, search = '', role = 'all', is_banned = 'all' }) => ({
        url: "/admin-api/user-management/",
        params: {
          page,
          ...(search ? {search}:{}),
          ...(role !== 'all' ? {role}:{}),
          ...(is_banned !== 'all' ? {is_banned}:{}),
        },
        method: "GET",
      }),
      providesTags: (result)=>
        result ? [
          {
            type: "User", id: "LIST"
          },
          ...result.results.map(({id})=> ({type: "User" as const, id}))
        ] : [{type: "User", id: "LIST"}],
    }),
  }),
});

export const {
  // auth endpoints
  useLoginMutation,
  // user endpoints
  useGetUsersQuery,
} = apiSlice;
