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
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { RefreshCw } from "lucide-react";

interface UserRanking {
  id: string;
  rank: number;
  userName: string;
  level: number;
  totalPoints: string;
}

// Dummy data
const generateDummyRankings = (): UserRanking[] => {
  return [
    {
      id: "1",
      rank: 1,
      userName: "Christine Brooks",
      level: 32,
      totalPoints: "2025-01-15",
    },
    {
      id: "2",
      rank: 2,
      userName: "Sarah Johnson",
      level: 28,
      totalPoints: "2025-02-10",
    },
    {
      id: "3",
      rank: 3,
      userName: "Lisa Davis",
      level: 15,
      totalPoints: "2025-03-15",
    },
    {
      id: "4",
      rank: 4,
      userName: "Stephanie Nixon",
      level: 22,
      totalPoints: "2021-04-05",
    },
    {
      id: "5",
      rank: 5,
      userName: "Stephanie Nixon",
      level: 30,
      totalPoints: "2025-04-10",
    },
    {
      id: "6",
      rank: 6,
      userName: "Kurt Bates",
      level: 25,
      totalPoints: "2025-05-15",
    },
    {
      id: "7",
      rank: 7,
      userName: "Autumn Pattison",
      level: 18,
      totalPoints: "2025-06-16",
    },
    {
      id: "8",
      rank: 8,
      userName: "Michael Chen",
      level: 8,
      totalPoints: "2025-07-20",
    },
    {
      id: "9",
      rank: 9,
      userName: "Emily Roberts",
      level: 12,
      totalPoints: "2025-08-12",
    },
    {
      id: "10",
      rank: 10,
      userName: "David Wilson",
      level: 35,
      totalPoints: "2025-09-05",
    },
    {
      id: "11",
      rank: 11,
      userName: "Jessica Martinez",
      level: 27,
      totalPoints: "2025-10-18",
    },
    {
      id: "12",
      rank: 12,
      userName: "Robert Taylor",
      level: 5,
      totalPoints: "2025-11-22",
    },
  ];
};

function RankingTable() {
  const [rankings] = useState<UserRanking[]>(generateDummyRankings());
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 10;

  // Pagination
  const totalPages = Math.ceil(rankings.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedRankings = rankings.slice(startIndex, endIndex);

  // Generate Level Badge Colors
  const getLevelBadgeClass = (level: number) => {
    if (level < 10) {
      return "bg-red-300 text-red-700 hover:bg-red-600";
    } else if (level < 20) {
      return "bg-yellow-100 text-yellow-700 hover:bg-yellow-100";
    } else if (level < 30) {
      return "bg-green-100 text-green-700 hover:bg-green-100";
    } else {
      return "bg-blue-100 text-blue-700 hover:bg-blue-100";
    }
  };

  // Status Text
  const getStatus = (level: number): string => {
    if (level < 20) {
      return "Need to Level Up";
    }
    return "Normal";
  };

  // Status Badge Colors
  const getStatusBadgeClass = (level: number) => {
    if (level < 20) {
      return "bg-red-100 text-red-700 hover:bg-red-100";
    }
    return "bg-green-100 text-green-700 hover:bg-green-100";
  };

  return (
    <div className="mt-4 md:mt-6">
      <div>
        <Card className="bg-transparent shadow-none border-none">
          <CardHeader className="px-0 ">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <h2 className="text-xl font-semibold">User Ranking & Performance</h2>
              <Button size={"lg"} className="bg-blue-600 hover:bg-blue-700">
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh Data
              </Button>
            </div>
          </CardHeader>
          <CardContent className="px-0">
            <div className="border rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <Table className="bg-white">
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHead className=" text-center">Rank</TableHead>
                      <TableHead className="pl-16">User</TableHead>
                      <TableHead className="">Level</TableHead>
                      <TableHead className="">Total Points</TableHead>
                      <TableHead className="">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedRankings.map((ranking) => (
                      <TableRow key={ranking.id} className="hover:bg-gray-50">
                        <TableCell className="text-center font-medium">
                          #{ranking.rank}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                              <svg
                                className="w-5 h-5 text-gray-500"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            </div>
                            <span className="font-medium text-sm">
                              {ranking.userName}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="cursor-pointer">
                          <Badge
                            variant="secondary"
                            className={`${getLevelBadgeClass(ranking.level)} font-medium`}
                          >
                            Level {ranking.level}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {ranking.totalPoints}
                        </TableCell>
                        <TableCell className="cursor-pointer">
                          <Badge
                            variant="secondary"
                            className={`${getStatusBadgeClass(ranking.level)} font-medium`}
                          >
                            {getStatus(ranking.level)}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-6 flex justify-end">
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
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default RankingTable;
