// components/moderation/ModerationTable.tsx
"use client";

import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { MoreVertical, Ban, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { useBanUserMutation, useGetModerationDataQuery, useUnbanUserMutation } from "@/store/slices/api/moderationApiSlice";

const ModerationTable = () => {
  const [filter, setFilter] = useState<string>("all");
  const [page, setPage] = useState(1);

  const { data, isLoading, isFetching } = useGetModerationDataQuery({
    page,
    filter,
  });

  const [banUser] = useBanUserMutation();
  const [unbanUser] = useUnbanUserMutation();

  const users = data?.users || [];
  const totalUsers = data?.top.total_user || 0;
  const itemsPerPage = 10;
  const totalPages = Math.ceil(totalUsers / itemsPerPage);

  const handleBan = async (userId: string) => {
    try {
      await banUser({ user_id: userId }).unwrap();
      toast.success("User banned");
    } catch (err: any) {
      toast.error(err?.data?.error || "Failed to ban");
    }
  };

  const handleUnban = async (userId: string) => {
    try {
      await unbanUser({ user_id: userId }).unwrap();
      toast.success("User unbanned");
    } catch (err: any) {
      toast.error(err?.data?.error || "Failed to unban");
    }
  };

  const getInitials = (first: string, last: string) =>
    `${first[0] || ""}${last[0] || ""}`.toUpperCase();

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pageNumbers = [];
    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
        pageNumbers.push(
          <PaginationItem key={i}>
            <PaginationLink
              isActive={page === i}
              onClick={() => setPage(i)}
              className="cursor-pointer"
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      } else if (i === page - 2 || i === page + 2) {
        pageNumbers.push(
          <PaginationItem key={i}>
            <PaginationEllipsis />
          </PaginationItem>
        );
      }
    }

    return (
      <Pagination className="mt-6">
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className={
                page === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"
              }
            />
          </PaginationItem>

          {pageNumbers}

          <PaginationItem>
            <PaginationNext
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className={
                page === totalPages
                  ? "pointer-events-none opacity-50"
                  : "cursor-pointer"
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    );
  };

  const UserCard = ({ user }: { user: (typeof users)[0] }) => (
    <div className="bg-white border rounded-xl p-4 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <Avatar className="h-12 w-12">
            <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-semibold">
              {getInitials(user.first_name, user.last_name)}
            </AvatarFallback>
          </Avatar>
          <div>
            <h4 className="font-semibold text-gray-900">
              {user.first_name} {user.last_name}
            </h4>
            <p className="text-xs text-gray-500">{user.role}</p>
          </div>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {user.is_banned ? (
              <DropdownMenuItem
                onClick={() => handleUnban(user.id)}
                className="text-green-600"
              >
                <CheckCircle className="mr-2 h-4 w-4" /> Unban User
              </DropdownMenuItem>
            ) : (
              <DropdownMenuItem
                onClick={() => handleBan(user.id)}
                className="text-red-600"
              >
                <Ban className="mr-2 h-4 w-4" /> Ban User
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <span className="text-gray-500">Status:</span>
          <span
            className={`ml-2 font-medium ${
              user.is_banned ? "text-red-600" : "text-green-600"
            }`}
          >
            {user.is_banned ? "Banned" : "Active"}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Warnings:</span>
          <span className="ml-2 font-medium">{user.warning}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="w-full rounded-lg bg-gray-50 p-4 md:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-xl font-semibold">User Moderation</h2>

        <Select
          value={filter}
          onValueChange={(v) => {
            setFilter(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Users</SelectItem>
            <SelectItem value="student">Students</SelectItem>
            <SelectItem value="teacher">Teachers</SelectItem>
            <SelectItem value="banned">Banned Only</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Loading State */}
      {isLoading || isFetching ? (
        <div className="text-center py-12 text-gray-500">Loading users...</div>
      ) : users.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No users found</div>
      ) : (
        <>
          {/* Desktop Table */}
          <div className="hidden md:block overflow-x-auto border rounded-lg bg-white">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Warnings</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                            {getInitials(user.first_name, user.last_name)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">
                            {user.first_name} {user.last_name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {user.id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="capitalize">{user.role}</TableCell>
                    <TableCell>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          user.is_banned
                            ? "bg-red-100 text-red-700"
                            : "bg-green-100 text-green-700"
                        }`}
                      >
                        {user.is_banned ? "Banned" : "Active"}
                      </span>
                    </TableCell>
                    <TableCell className="text-center font-medium">
                      {user.warning}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {user.is_banned ? (
                            <DropdownMenuItem
                              onClick={() => handleUnban(user.id)}
                              className="text-green-600"
                            >
                              <CheckCircle className="mr-2 h-4 w-4" /> Unban
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem
                              onClick={() => handleBan(user.id)}
                              className="text-red-600"
                            >
                              <Ban className="mr-2 h-4 w-4" /> Ban User
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Mobile Cards */}
          <div className="md:hidden space-y-4">
            {users.map((user) => (
              <UserCard key={user.id} user={user} />
            ))}
          </div>

          {/* Pagination - Both Views */}
          {renderPagination()}
        </>
      )}
    </div>
  );
};

export default ModerationTable;
