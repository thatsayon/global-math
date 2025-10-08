"use client"
import React, { useState } from "react";
import { Card, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";
import { RefreshCw, Send, User } from "lucide-react";
import { toast } from "sonner";

interface SupportMessage {
  id: string;
  title: string;
  userName: string;
  userRole: "Student" | "Teacher";
  message: string;
  timestamp: string;
}

// Dummy data
const generateDummyMessages = (): SupportMessage[] => {
  return [
    {
      id: "1",
      title: "Can not access to my account after password reset",
      userName: "Sarah Johnson",
      userRole: "Student",
      message: "I tried to reset my password but the email never arrived. When i tried to log in with my old password ot says account locked",
      timestamp: "2 minutes ago",
    },
    {
      id: "2",
      title: "Challenges not marked as complete",
      userName: "Michael Chan",
      userRole: "Student",
      message: "I complete the Math Challenge #5 but it's still showing as incomplete in my dashboard. I submitted all answers correctly.",
      timestamp: "2 minutes ago",
    },
    {
      id: "3",
      title: "Request for advanced class management features",
      userName: "Dr. Lisa Devis",
      userRole: "Teacher",
      message: "Would like to request bulk student import and functionality for easier class management. Currently managing 150+ students manually.",
      timestamp: "2 minutes ago",
    },
    {
      id: "4",
      title: "Inappropriate content reported in study group",
      userName: "Tom Anderson",
      userRole: "Student",
      message: "There's inappropriate content being shared in the Geometrics Study Grope. I've tried to report it through the app but nothing happened.",
      timestamp: "2 minutes ago",
    },
    {
      id: "5",
      title: "App crashes when uploading large files",
      userName: "Prof. Robert Tayler",
      userRole: "Teacher",
      message: "The app crashes every time i try to upload files larger than 10MB. This is affecting my ability to share course materials.",
      timestamp: "2 minutes ago",
    },
    {
      id: "6",
      title: "Unable to join live class sessions",
      userName: "Emma Wilson",
      userRole: "Student",
      message: "I keep getting an error when trying to join the live class. It says 'connection failed'. My internet is working fine.",
      timestamp: "5 minutes ago",
    },
    {
      id: "7",
      title: "Grading system showing incorrect scores",
      userName: "Prof. James Miller",
      userRole: "Teacher",
      message: "The grading system is calculating student scores incorrectly. Several students have reported discrepancies.",
      timestamp: "10 minutes ago",
    },
    {
      id: "8",
      title: "Cannot download course materials",
      userName: "Alex Brown",
      userRole: "Student",
      message: "When I try to download the PDF materials, I get a 404 error. This has been happening for the past 2 days.",
      timestamp: "15 minutes ago",
    },
    {
      id: "9",
      title: "Mobile app not syncing with web version",
      userName: "Jennifer Lee",
      userRole: "Teacher",
      message: "Changes I make on the mobile app don't appear on the web version. This is causing confusion with my students.",
      timestamp: "20 minutes ago",
    },
    {
      id: "10",
      title: "Payment processing issue for premium subscription",
      userName: "David Garcia",
      userRole: "Student",
      message: "I've been charged twice for my premium subscription this month. Need help getting a refund for the duplicate charge.",
      timestamp: "25 minutes ago",
    },
  ];
};

function SupportTable() {
  const [messages] = useState<SupportMessage[]>(generateDummyMessages());
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedMessage, setSelectedMessage] = useState<SupportMessage | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [replyMessage, setReplyMessage] = useState<string>("");
  const [isSending, setIsSending] = useState<boolean>(false);
  const itemsPerPage = 5;

  // Pagination
  const totalPages = Math.ceil(messages.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedMessages = messages.slice(startIndex, endIndex);

  const handleSendMessage = (message: SupportMessage) => {
    setSelectedMessage(message);
    setIsDialogOpen(true);
    setReplyMessage("");
  };

  const handleSubmitReply = () => {
    if (!replyMessage.trim()) {
      toast.error("Please write a message before sending");
      return;
    }

    setIsSending(true);

    const sendPromise = new Promise<{ success: boolean }>((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 2000);
    });

    toast.promise(sendPromise, {
      loading: "Sending message...",
      success: () => {
        setIsSending(false);
        setIsDialogOpen(false);
        setReplyMessage("");
        return "Message sent successfully";
      },
      error: "Failed to send message",
    });
  };

  return (
    <div className="mt-4 md:mt-6 lg:mt-8">
      <div>
        <div className="mb-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <h2 className="text-xl font-semibold">
              All messages ({messages.length})
            </h2>
            <Button className="bg-blue-500 hover:bg-blue-600">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh Data
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          {paginatedMessages.map((message) => (
            <Card key={message.id} className="hover:shadow-md transition-shadow">
              <CardContent className="">
                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                      <User className="w-5 h-5 text-gray-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-base md:text-lg mb-2 break-words">
                        {message.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600 mb-3">
                        <span className="font-medium">{message.userName}</span>
                        <span>•</span>
                        <span>{message.userRole}</span>
                      </div>
                      <p className="text-sm text-gray-700 break-words">
                        {message.message}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row lg:flex-col items-start sm:items-center lg:items-end gap-3 lg:ml-4">
                    <span className="text-sm text-gray-500 whitespace-nowrap">
                      {message.timestamp}
                    </span>
                    <Button
                      onClick={() => handleSendMessage(message)}
                      className="bg-blue-500 hover:bg-blue-600 w-full sm:w-auto"
                    >
                      <Send className="mr-2 h-4 w-4" />
                      Send message
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center">
            <Pagination className="flex justify-end">
              <PaginationContent>
                <PaginationItem className="border-2 rounded-lg">
                  <PaginationPrevious
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    className={
                      currentPage === 1
                        ? "pointer-events-none opacity-50"
                        : "cursor-pointer"
                    }
                  />
                </PaginationItem>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
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
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    className={
                      currentPage === totalPages
                        ? "pointer-events-none opacity-50"
                        : "cursor-pointer"
                    }
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        )}

        {/* Reply Dialog */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle className="text-lg font-semibold">
                Reply to Message
              </DialogTitle>
            </DialogHeader>
            {selectedMessage && (
              <div className="space-y-4 mt-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <User className="w-5 h-5 text-gray-500" />
                    <span className="font-medium">{selectedMessage.userName}</span>
                    <span className="text-sm text-gray-500">• {selectedMessage.userRole}</span>
                  </div>
                  <h4 className="font-semibold mb-2">{selectedMessage.title}</h4>
                  <p className="text-sm text-gray-700">{selectedMessage.message}</p>
                </div>

                <div className="space-y-2">
                  <Textarea
                    placeholder="Write message........."
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                    className="min-h-[150px] resize-none"
                    disabled={isSending}
                  />
                </div>

                <div className="flex justify-center">
                  <Button
                    onClick={handleSubmitReply}
                    disabled={isSending}
                    className="bg-blue-500 hover:bg-blue-600 px-8"
                  >
                    <Send className="mr-2 h-4 w-4" />
                    Send message
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

export default SupportTable;