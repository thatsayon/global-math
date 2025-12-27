
import { apiSlice } from "@/store/slices/api/ApiSlice";
import {
  PointAdjustment,
  PointAdjustmentUpdateRequest,
  PointAdjustmentUpdateResponse,
} from "@/types/point.type";

export const pointApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // Get current point settings
    getPointAdjustment: builder.query<PointAdjustment, void>({
      query: () => "/admin-api/point-adjustment/",
      providesTags: ["PointAdjustment"],
    }),

    // Update point settings
    updatePointAdjustment: builder.mutation<
      PointAdjustmentUpdateResponse,
      PointAdjustmentUpdateRequest
    >({
      query: (body) => ({
        url: "/admin-api/point-adjustment/",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["PointAdjustment"],
    }),
  }),
});

export const {
  useGetPointAdjustmentQuery,
  useUpdatePointAdjustmentMutation,
} = pointApiSlice;