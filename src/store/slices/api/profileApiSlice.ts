import { apiSlice } from "./ApiSlice";
import {
  ProfileResponse,
  UpdateProfileRequest,
  UpdateProfileResponse,
  ChangePasswordRequest,
  ChangePasswordResponse,
  MathLevelsResponse,
  CreateLevelRequest,
  CreateLevelResponse,
  UpdateLevelRequest,
  UpdateLevelResponse,
} from "@/types/settings.type";

export const profileApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // Profile Endpoints
    getProfile: builder.query<ProfileResponse, void>({
      query: () => "/admin-api/profile/",
      providesTags: ["Profile"],
    }),

    updateProfile: builder.mutation<UpdateProfileResponse, UpdateProfileRequest>({
      query: (data) => {
        const formData = new FormData();
        if (data.first_name) formData.append("first_name", data.first_name);
        if (data.last_name) formData.append("last_name", data.last_name);
        if (data.profile_pic) formData.append("profile_pic", data.profile_pic);
        if (data.profile_pic === null) formData.append("profile_pic", "");

        return {
          url: "/admin-api/profile/",
          method: "PATCH",
          body: formData,
        };
      },
      invalidatesTags: ["Profile"],
    }),

    changePassword: builder.mutation<ChangePasswordResponse, ChangePasswordRequest>({
      query: (body) => ({
        url: "/admin-api/update-password/",
        method: "PATCH",
        body,
      }),
    }),

    // Level Adjustment Endpoints
    getMathLevels: builder.query<MathLevelsResponse, void>({
      query: () => "/admin-api/level-adjustment/",
      providesTags: ["Level"]
    }),

    createMathLevel: builder.mutation<CreateLevelResponse, CreateLevelRequest>({
      query: (body) => ({
        url: "/admin-api/level-adjustment/",
        method: "POST",
        body,
        credentials: "include"
      }),
      invalidatesTags: ["Level"],
    }),

    updateMathLevel: builder.mutation<UpdateLevelResponse, { id: string; data: UpdateLevelRequest }>({
      query: ({ id, data }) => ({
        url: `/admin-api/level-adjustment/${id}/`,
        method: "PATCH",
        body: data,
        credentials: "include"
      }),
      invalidatesTags: ["Level"]
    }),
  }),
  overrideExisting: false
});

export const {
  useGetProfileQuery,
  useUpdateProfileMutation,
  useChangePasswordMutation,
  useGetMathLevelsQuery,
  useCreateMathLevelMutation,
  useUpdateMathLevelMutation,
} = profileApiSlice;