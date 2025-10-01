"use client"
import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "../ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";
import { Badge } from "../ui/badge";
import { Calendar } from "../ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../ui/popover";
import { Button } from "../ui/button";
import { ChevronDown } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

type Challenge = {
  id: string;
  question: string;
  answer: string;
  subject: string;
  status: "Published" | "Pending";
  publishDate: Date;
};

// Dummy data
const generateDummyChallenges = (): Challenge[] => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const twoDaysAgo = new Date(today);
  twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const nextWeek = new Date(today);
  nextWeek.setDate(nextWeek.getDate() + 7);

  return [
    {
      id: "1",
      question: "Simplify: 12-(3+5)-2[2 - (3 + 5)] times 2[2-(3+5)-2",
      answer: "12-(3+5)x2-12-8x2-12-16-4",
      subject: "Pre- Algebra Level 1",
      status: "Pending",
      publishDate: tomorrow,
    },
    {
      id: "2",
      question: "A pack has 48 pencils. If 12 students share them equally, how many pencils per student?",
      answer: "48÷12=4 pencils",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: yesterday,
    },
    {
      id: "3",
      question: "If one notebook costs $7, how much will 5 notebooks cost?",
      answer: "5 notebooks × $7 each = $35.",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: twoDaysAgo,
    },
    {
      id: "4",
      question: "A box has 36 candies. If 9 kids share them equally, how many candies does each get?",
      answer: "36 candies ÷ 9 kids = 4 candies per kid.",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: new Date(2025, 3, 5),
    },
    {
      id: "5",
      question: "A pack has 48 pencils. If 12 students share them equally, how many pencils per student?",
      answer: "Pattern multiples by 2: next three terms are 80, 160, 320.",
      subject: "Pre- Algebra Level 1",
      status: "Pending",
      publishDate: tomorrow,
    },
    {
      id: "6",
      question: "If a pizza costs $15 and you have $60, how many pizzas can you buy?",
      answer: "60÷15=4 pizzas",
      subject: "Pre- Algebra Level 1",
      status: "Pending",
      publishDate: nextWeek,
    },
    {
      id: "7",
      question: "What is 25% of 200?",
      answer: "50",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: yesterday,
    },
    {
      id: "8",
      question: "Solve: 3x + 7 = 22",
      answer: "x = 5",
      subject: "Pre- Algebra Level 1",
      status: "Pending",
      publishDate: new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000),
    },
    {
      id: "9",
      question: "What is the perimeter of a rectangle with length 8 and width 5?",
      answer: "26 units",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: new Date(2025, 2, 15),
    },
    {
      id: "10",
      question: "If 5 apples cost $10, how much does 1 apple cost?",
      answer: "$2",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: new Date(2025, 1, 10),
    },
    {
      id: "11",
      question: "Solve: 3x + 7 = 22",
      answer: "x = 5",
      subject: "Pre- Algebra Level 1",
      status: "Pending",
      publishDate: new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000),
    },
    {
      id: "12",
      question: "What is the perimeter of a rectangle with length 8 and width 5?",
      answer: "26 units",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: new Date(2025, 2, 15),
    },
    {
      id: "13",
      question: "If 5 apples cost $10, how much does 1 apple cost?",
      answer: "$2",
      subject: "Pre- Algebra Level 1",
      status: "Published",
      publishDate: new Date(2025, 1, 10),
    },
  ];
};

function Challenges() {
  const [challenges, setChallenges] = useState<Challenge[]>(generateDummyChallenges());
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedSubject, setSelectedSubject] = useState<string>("all");
  const [openDatePicker, setOpenDatePicker] = useState<string | null>(null);
  const itemsPerPage = 10;

  // Get unique subjects
  const subjects = ["all", ...Array.from(new Set(challenges.map(c => c.subject)))];

  // Filter challenges
  const filteredChallenges = challenges.filter(challenge => 
    selectedSubject === "all" || challenge.subject === selectedSubject
  );

  // Pagination
  const totalPages = Math.ceil(filteredChallenges.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedChallenges = filteredChallenges.slice(startIndex, endIndex);

  const handleDateChange = (challengeId: string, newDate: Date | undefined) => {
    if (!newDate) return;

    setOpenDatePicker(null);

    const updatePromise = new Promise<{ date: string }>((resolve) => {
      setTimeout(() => {
        setChallenges(prev => 
          prev.map(challenge => {
            if (challenge.id === challengeId) {
              const today = new Date();
              today.setHours(0, 0, 0, 0);
              const selectedDate = new Date(newDate);
              selectedDate.setHours(0, 0, 0, 0);
              
              return {
                ...challenge,
                publishDate: newDate,
                status: selectedDate <= today ? "Published" : "Pending"
              };
            }
            return challenge;
          })
        );
        resolve({ date: format(newDate, "PPP") });
      }, 1500);
    });

    toast.promise(updatePromise, {
      loading: "Updating publish date...",
      success: (data: { date: string }) => {
        return `Publish date updated to ${data.date}`;
      },
      error: "Failed to update publish date",
    });
  };

  return (
    <div className="mt-4 md:mt-6 lg:mt-8">
      <div>
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <h2 className="text-xl font-semibold">Daily Challenges</h2>
              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <SelectValue placeholder="Math Subjects" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Subjects</SelectItem>
                  {subjects.slice(1).map(subject => (
                    <SelectItem key={subject} value={subject}>
                      {subject}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="border rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHead className="w-12">No</TableHead>
                      <TableHead className="min-w-[250px]">Question</TableHead>
                      <TableHead className="min-w-[200px]">Answer</TableHead>
                      <TableHead className="w-40">Subject</TableHead>
                      <TableHead className="w-28">Status</TableHead>
                      <TableHead className="w-32">Time Stamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedChallenges.map((challenge, index) => (
                      <TableRow key={challenge.id}>
                        <TableCell className="font-medium">
                          {startIndex + index + 1}
                        </TableCell>
                        <TableCell className="text-sm">
                          {challenge.question}
                        </TableCell>
                        <TableCell className="text-sm">
                          {challenge.answer}
                        </TableCell>
                        <TableCell>
                          <span className="text-xs">
                            {challenge.subject}
                          </span>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={challenge.status === "Published" ? "default" : "secondary"}
                            className={
                              challenge.status === "Published" 
                                ? "bg-green-500 hover:bg-green-600" 
                                : "bg-orange-500 hover:bg-orange-600"
                            }
                          >
                            {challenge.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {challenge.status === "Pending" ? (
                            <Popover 
                              open={openDatePicker === challenge.id}
                              onOpenChange={(open) => setOpenDatePicker(open ? challenge.id : null)}
                            >
                              <PopoverTrigger asChild>
                                <Button
                                  variant="ghost"
                                  className="w-full justify-between px-2 py-1 h-auto text-xs hover:bg-gray-100"
                                >
                                  {format(challenge.publishDate, "yyyy-MM-dd")}
                                  <ChevronDown className="ml-1 h-3 w-3" />
                                </Button>
                              </PopoverTrigger>
                              <PopoverContent className="w-auto p-0" align="end">
                                <Calendar
                                  mode="single"
                                  selected={challenge.publishDate}
                                  onSelect={(date) => handleDateChange(challenge.id, date)}
                                  initialFocus
                                />
                              </PopoverContent>
                            </Popover>
                          ) : (
                            <span className="text-xs text-gray-600">
                              {format(challenge.publishDate, "yyyy-MM-dd")}
                            </span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-6 flex justify-center">
                <Pagination>
                  <PaginationContent>
                    <PaginationItem>
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
                      <PaginationItem key={page}>
                        <PaginationLink
                          onClick={() => setCurrentPage(page)}
                          isActive={currentPage === page}
                          className="cursor-pointer"
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    ))}
                    
                    <PaginationItem>
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
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default Challenges;