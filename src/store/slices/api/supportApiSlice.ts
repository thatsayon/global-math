import {
  SupportConversationListResponse,
  SupportMessagesResponse,
  SupportReplyRequest,
  SupportReplyResponse,
} from "@/types/support.type";
import { apiSlice } from "./ApiSlice";

export const supportApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // Get all conversations
    getSupportConversations: builder.query<
      SupportConversationListResponse,
      { page?: number }
    >({
      query: ({ page = 1 }) => ({
        url: "/admin-api/support-message/",
        params: { page },
      }),
      providesTags: ["Conversation"]
    }),

    // Get full conversation by ID
    getSupportMessages: builder.query<SupportMessagesResponse, string>({
      query: (conversationId) => `/admin-api/support-message/${conversationId}/`,
      providesTags: ["Conversation"]
    }),

    // Send reply
    sendSupportReply: builder.mutation<
      SupportReplyResponse,
      { conversationId: string; body: SupportReplyRequest }
    >({
      query: ({ conversationId, body }) => ({
        url: `/admin-api/support-message-reply/${conversationId}/`,
        method: "POST",
        body,
      }),
      invalidatesTags: ["Conversation"]
    }),
  }),
});

export const {
  useGetSupportConversationsQuery,
  useSendSupportReplyMutation,
  useLazyGetSupportMessagesQuery
} = supportApiSlice;