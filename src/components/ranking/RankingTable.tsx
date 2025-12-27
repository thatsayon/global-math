"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw } from "lucide-react";

import { useGetLeaderboardQuery } from "@/store/slices/api/leaderboardApiSlice";

// Format status: "need_to_level_up" → "Need To Level Up"
const formatStatus = (status: string) => {
  return status
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

// Level badge colors (same as your static logic)
const getLevelBadgeClass = (level: number) => {
  if (level < 10) return "bg-red-300 text-red-700 hover:bg-red-600";
  if (level < 20) return "bg-yellow-100 text-yellow-700 hover:bg-yellow-100";
  if (level < 30) return "bg-green-100 text-green-700 hover:bg-green-100";
  return "bg-blue-100 text-blue-700 hover:bg-blue-100";
};

// Status badge colors (red if needs leveling up)
const getStatusBadgeClass = (status: string) => {
  return status.includes("need_to_level_up")
    ? "bg-red-100 text-red-700 hover:bg-red-100"
    : "bg-green-100 text-green-700 hover:bg-green-100";
};

function RankingTable() {
  const [currentPage, setCurrentPage] = useState(1);

  const {
    data: leaderboardData,
    isLoading,
    isFetching,
    refetch,
  } = useGetLeaderboardQuery();

  const users = leaderboardData?.results || [];
  const totalCount = leaderboardData?.count || 0;
  const itemsPerPage = 10;
  const totalPages = Math.ceil(totalCount / itemsPerPage);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedUsers = users.slice(startIndex, endIndex);

  return (
    <div className="mt-4 md:mt-6">
      <div>
        <Card className="bg-transparent shadow-none border-none">
          <CardHeader className="px-0">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <h2 className="text-xl font-semibold">
                User Ranking & Performance ({totalCount})
              </h2>
              <Button
                size="lg"
                onClick={() => refetch()}
                className="bg-blue-600 hover:bg-blue-700"
                disabled={isFetching}
              >
                <RefreshCw
                  className={`mr-2 h-4 w-4 ${isFetching ? "animate-spin" : ""}`}
                />
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
                      <TableHead className="text-center">Rank</TableHead>
                      <TableHead className="pl-16">User</TableHead>
                      <TableHead className="">Level</TableHead>
                      <TableHead className="">Total Points</TableHead>
                      <TableHead className="">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8">
                          Loading rankings...
                        </TableCell>
                      </TableRow>
                    ) : paginatedUsers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8">
                          No users in leaderboard yet
                        </TableCell>
                      </TableRow>
                    ) : (
                      paginatedUsers.map((user) => (
                        <TableRow key={user.user_id} className="hover:bg-gray-50">
                          <TableCell className="text-center font-medium">
                            #{user.rank}
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
                                {user.username}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="cursor-pointer">
                            <Badge
                              variant="secondary"
                              className={`${getLevelBadgeClass(user.level)} font-medium`}
                            >
                              Level {user.level}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {user.total_points.toLocaleString()}
                          </TableCell>
                          <TableCell className="cursor-pointer">
                            <Badge
                              variant="secondary"
                              className={`${getStatusBadgeClass(user.status)} font-medium`}
                            >
                              {formatStatus(user.status)}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-6 flex justify-end">
                <Pagination>
                  <PaginationContent>
                    <PaginationItem className="border-2 rounded-lg">
                      <PaginationPrevious
                        onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                        className={
                          currentPage === 1
                            ? "pointer-events-none opacity-50"
                            : "cursor-pointer"
                        }
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