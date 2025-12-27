"use client";

import React, { useState } from "react";
import { ChevronLeft, ChevronRight, Trophy, User } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { EngagementUser, StudentEngagement } from "@/types/analytics.type";

interface EngagementTableProps {
  engagementData: StudentEngagement;
  currentPage: number;
  onPageChange: (page: number) => void;
}

const EngagementTable: React.FC<EngagementTableProps> = ({
  engagementData,
  currentPage,
  onPageChange,
}) => {
  const [selectedUserType, setSelectedUserType] = useState<"All" | "student" | "teacher">("All");

  const users = engagementData.results || [];
  const totalCount = engagementData.count || 0;
  const itemsPerPage = 5; // Match your UI (5 rows per page)
  const totalPages = Math.ceil(totalCount / itemsPerPage);

  // Client-side filter by role
  const filteredUsers = users.filter((user) =>
    selectedUserType === "All" ? true : user.role === selectedUserType
  );

  // But we display only the current API page's data (already paginated server-side)
  // We use the full results from API for the current page
  const displayedUsers = users;

  const getScoreColor = (score: number) => {
    if (score >= 90) return "bg-green-100 text-green-700";
    if (score >= 80) return "bg-blue-100 text-blue-700";
    return "bg-gray-100 text-gray-700";
  };

  if (displayedUsers.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="py-12 text-center text-gray-500">
          No engagement data available
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <CardTitle>Student Engagement Analytics</CardTitle>
          <Select value={selectedUserType} onValueChange={(v) => setSelectedUserType(v as "All" | "student" | "teacher")}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Select User Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All</SelectItem>
              <SelectItem value="student">Student</SelectItem>
              <SelectItem value="teacher">Teacher</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[60px]">No</TableHead>
                <TableHead>User</TableHead>
                <TableHead className="text-center">Challenges</TableHead>
                <TableHead className="text-center">Engagement Score</TableHead>
                <TableHead>Last Active</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayedUsers
                .filter((user) =>
                  selectedUserType === "All" ? true : user.role === selectedUserType
                )
                .map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-medium">{row.no}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={row.profile_pic || undefined} alt={row.name} />
                          <AvatarFallback>
                            <User className="h-5 w-5" />
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium text-sm">{row.name}</div>
                          <div className="text-xs text-gray-500 capitalize">{row.role}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center space-x-1">
                        <Trophy className="h-4 w-4 text-gray-400" />
                        <span>{row.challenges}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <span
                        className={`px-3 py-1 inline-flex text-xs font-semibold rounded-full ${getScoreColor(
                          row.engagement_score
                        )}`}
                      >
                        {row.engagement_score}%
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {row.last_active
                        ? new Date(row.last_active).toLocaleDateString()
                        : "—"}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-end space-x-2 py-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft />
            </Button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={currentPage === page ? "default" : "outline"}
                size="sm"
                onClick={() => onPageChange(page)}
              >
                {page}
              </Button>
            ))}

            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EngagementTable;