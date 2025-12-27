"use client";

import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { RefreshCw, Send, User } from "lucide-react";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";

import {
  useGetSupportConversationsQuery,
  useLazyGetSupportMessagesQuery,
  useSendSupportReplyMutation,
} from "@/store/slices/api/supportApiSlice";
import { SupportConversation, SupportMessage } from "@/types/support.type";

function SupportTable() {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedConversation, setSelectedConversation] = useState<SupportConversation | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [replyMessage, setReplyMessage] = useState("");

  const {
    data: conversationsData,
    isLoading,
    isFetching,
    refetch,
  } = useGetSupportConversationsQuery({ page: currentPage });

  const [getMessages, { data: messagesData, isFetching: isFetchingMessages }] =
    useLazyGetSupportMessagesQuery();

  const [sendReply, { isLoading: isSending }] = useSendSupportReplyMutation();

  const conversations = conversationsData?.results || [];
  const totalCount = conversationsData?.count || 0;
  const itemsPerPage = 5;
  const totalPages = Math.ceil(totalCount / itemsPerPage);

  const messages = messagesData?.results || [];

  const openConversation = async (conv: SupportConversation) => {
    setSelectedConversation(conv);
    setIsDialogOpen(true);
    setReplyMessage("");
    await getMessages(conv.id);
  };

  const handleSendReply = async () => {
    if (!replyMessage.trim() || !selectedConversation) {
      toast.error("Please write a message");
      return;
    }

    try {
      await sendReply({
        conversationId: selectedConversation.id,
        body: { message: replyMessage },
      }).unwrap();

      toast.success("Message sent successfully");
      setReplyMessage("");
      await getMessages(selectedConversation.id);
    } catch {
      toast.error("Failed to send message");
    }
  };

  const isAdminMessage = (msg: SupportMessage) => msg.sender_role === "";

  return (
    <div className="mt-4 md:mt-6 lg:mt-8">
      <div>
        <div className="mb-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <h2 className="text-xl font-semibold">
              All messages ({totalCount})
            </h2>
            <Button onClick={() => refetch()} className="bg-blue-500 hover:bg-blue-600">
              <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? "animate-spin" : ""}`} />
              Refresh Data
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Loading conversations...</div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No support messages</div>
          ) : (
            conversations.map((conv) => (
              <Card
                key={conv.id}
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => openConversation(conv)}
              >
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                        <User className="w-5 h-5 text-gray-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600 mb-2">
                          <span className="font-medium">{conv.user_name}</span>
                          <span>•</span>
                          <span className="capitalize">{conv.user_role}</span>
                          {!conv.is_closed && (
                            <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                              Open
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 break-words line-clamp-2">
                          {conv.last_message}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-3">
                      <span className="text-sm text-gray-500 whitespace-nowrap">
                        {formatDistanceToNow(new Date(conv.last_message_time), { addSuffix: true })}
                      </span>
                      <Button
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent card click
                          openConversation(conv);
                        }}
                        className="bg-blue-500 hover:bg-blue-600 w-full sm:w-auto"
                      >
                        Open Conversation
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center">
            <Pagination>
              <PaginationContent>
                <PaginationItem className="border-2 rounded-lg">
                  <PaginationPrevious
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                  />
                </PaginationItem>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <PaginationItem className="border-2 rounded-lg" key={page}>
                    <PaginationLink
                      onClick={() => setCurrentPage(page)}
                      isActive={currentPage === page}
                      className="cursor-pointer"
                    >
                      {page}
                    </PaginationLink>
                  </PaginationItem>
                ))}

                <PaginationItem className="border-2 rounded-lg">
                  <PaginationNext
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        )}

        {/* Messenger-style Conversation Dialog */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="sm:max-w-[700px] max-h-[80vh] flex flex-col">
            <DialogHeader>
              <DialogTitle className="text-lg font-semibold">
                Conversation with {selectedConversation?.user_name}
              </DialogTitle>
            </DialogHeader>

            <div className="flex-1 overflow-y-auto py-4 space-y-4">
              {isFetchingMessages ? (
                <div className="text-center text-gray-500">Loading messages...</div>
              ) : messages.length === 0 ? (
                <div className="text-center text-gray-500">No messages yet</div>
              ) : (
                [...messages].reverse().map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${isAdminMessage(msg) ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg px-4 py-3 ${
                        isAdminMessage(msg)
                          ? "bg-blue-500 text-white"
                          : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <p className="text-sm break-words">{msg.message}</p>
                      <p className={`text-xs mt-1 ${isAdminMessage(msg) ? "text-blue-100" : "text-gray-500"}`}>
                        {formatDistanceToNow(new Date(msg.created_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="flex gap-3 pt-4 border-t">
              <Textarea
                placeholder="Write your reply..."
                value={replyMessage}
                onChange={(e) => setReplyMessage(e.target.value)}
                className="min-h-[80px] resize-none flex-1"
                disabled={isSending}
              />
              <Button
                onClick={handleSendReply}
                disabled={isSending || !replyMessage.trim()}
                className="h-auto self-end px-6"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

export default SupportTable;