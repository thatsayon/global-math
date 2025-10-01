"use client";
import React, { useState } from "react";
import { ChevronLeft, ChevronRight, MessageSquare, Trophy, User } from "lucide-react";
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

interface EngagementData {
  no: number;
  user: string;
  role: string;
  posts: number;
  comments: number;
  challenges: number;
  engagementScore: number;
  lastActive: string;
}

const engagementData: EngagementData[] = [
  { no: 1, user: "Christine Brooks", role: "Student", posts: 45, comments: 128, challenges: 23, engagementScore: 96, lastActive: "2025-01-15" },
  { no: 2, user: "Sarah Johnson", role: "Student", posts: 52, comments: 98, challenges: 18, engagementScore: 94, lastActive: "2025-02-10" },
  { no: 3, user: "Lisa Devis", role: "Teacher", posts: 44, comments: 56, challenges: 12, engagementScore: 88, lastActive: "2025-03-15" },
  { no: 4, user: "Stephanie Nicol", role: "Student", posts: 32, comments: 48, challenges: 31, engagementScore: 82, lastActive: "2025-04-05" },
  { no: 5, user: "Stephanie Nicol", role: "Teacher", posts: 22, comments: 22, challenges: 8, engagementScore: 92, lastActive: "2025-04-15" },
  { no: 6, user: "Kurt Bates", role: "Teacher", posts: 78, comments: 33, challenges: 12, engagementScore: 90, lastActive: "2025-05-15" },
  { no: 7, user: "Michael Chen", role: "Student", posts: 35, comments: 67, challenges: 15, engagementScore: 85, lastActive: "2025-03-20" },
  { no: 8, user: "Emma Wilson", role: "Student", posts: 41, comments: 89, challenges: 20, engagementScore: 91, lastActive: "2025-04-12" },
];

const EngagementTable: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedUserType, setSelectedUserType] = useState("All");

  const itemsPerPage = 5;

  // ✅ Filtering logic (works for All, Student, Teacher)
  const filteredData = engagementData.filter((item) =>
    selectedUserType === "All" ? true : item.role === selectedUserType
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredData.slice(
    startIndex,
    startIndex + itemsPerPage
  );

  const getScoreColor = (score: number) => {
    if (score >= 90) return "bg-green-100 text-green-700";
    if (score >= 80) return "bg-blue-100 text-blue-700";
    return "bg-gray-100 text-gray-700";
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <CardTitle>Student Engagement Analytics</CardTitle>

          <Select value={selectedUserType} onValueChange={setSelectedUserType}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Select User Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All</SelectItem>
              <SelectItem value="Student">Student</SelectItem>
              <SelectItem value="Teacher">Teacher</SelectItem>
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
                <TableHead className="text-center">Posts</TableHead>
                <TableHead className="text-center">Comments</TableHead>
                <TableHead className="text-center">Challenges</TableHead>
                <TableHead className="text-center">Engagement Score</TableHead>
                <TableHead>Last Active</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedData.map((row) => (
                <TableRow key={row.no}>
                  <TableCell className="font-medium">{row.no}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-gray-500" />
                      </div>
                      <div>
                        <div className="font-medium text-sm">{row.user}</div>
                        <div className="text-xs text-gray-500">{row.role}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="flex items-center justify-center space-x-1">
                      <MessageSquare className="h-4 w-4 text-gray-400" />
                      <span>{row.posts}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="flex items-center justify-center space-x-1">
                      <MessageSquare className="h-4 w-4 text-gray-400" />
                      <span>{row.comments}</span>
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
                        row.engagementScore
                      )}`}
                    >
                      {row.engagementScore}%
                    </span>
                  </TableCell>
                  <TableCell className="text-sm text-gray-500">
                    {row.lastActive}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-end space-x-2 py-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft/>
          </Button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <Button
              key={page}
              variant={currentPage === page ? "default" : "outline"}
              size="sm"
              onClick={() => setCurrentPage(page)}
            >
              {page}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setCurrentPage((prev) => Math.min(totalPages, prev + 1))
            }
            disabled={currentPage === totalPages}
          >
            <ChevronRight/>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default EngagementTable;
