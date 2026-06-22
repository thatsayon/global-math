"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Search, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { useGetUsersQuery } from "@/store/slices/api/ApiSlice";

const UserManagement: React.FC = () => {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<"all" | "student" | "teacher">(
    "all"
  );
  const [statusFilter, setStatusFilter] = useState<"all" | boolean>("all");
  const [searchInput, setSearchInput] = useState("");
  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(searchInput);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchInput]);

  const {
    data: usersData,
    isLoading,
    isFetching,
  } = useGetUsersQuery({
    page,
    search: searchQuery || undefined,
    role: roleFilter === "all" ? undefined : roleFilter,
    is_banned: statusFilter === "all" ? undefined : statusFilter,
  });

  // Reset page on filter change
  useEffect(() => {
    setPage(1);
  }, [searchQuery, roleFilter, statusFilter]);

  const totalPages = usersData?.count ? Math.ceil(usersData.count / 10) : 1; // assuming 10 per page

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const renderPaginationItems = () => {
    const items = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink onClick={() => setPage(i)} isActive={page === i}>
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }
    } else {
      if (page > 3) items.push(<PaginationEllipsis key="start-ellipsis" />);
      for (
        let i = Math.max(1, page - 2);
        i <= Math.min(totalPages, page + 2);
        i++
      ) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink onClick={() => setPage(i)} isActive={page === i}>
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }
      if (page < totalPages - 2)
        items.push(<PaginationEllipsis key="end-ellipsis" />);
    }

    return items;
  };

  return (
    <div className="p-8 min-h-screen bg-gray-50/30">
      <div className="max-w-[1920px] mx-auto">
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search users
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search by name, email or username..."
                  className="pl-10 min-h-11 max-w-[400px]"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <Select
                value={roleFilter}
                onValueChange={(v) => setRoleFilter(v as any)}
              >
                <SelectTrigger className="min-h-11 w-80">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All roles</SelectItem>
                  <SelectItem value="student">Student</SelectItem>
                  <SelectItem value="teacher">Teacher</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <Select
                value={statusFilter.toString()}
                onValueChange={(v) =>
                  setStatusFilter(v === "all" ? "all" : v === "true")
                }
              >
                <SelectTrigger className="min-h-11 w-80">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All status</SelectItem>
                  <SelectItem value="false">Active</SelectItem>
                  <SelectItem value="true">Banned</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-200 flex justify-between items-center bg-white">
            <h2 className="text-lg font-semibold text-gray-900">
              Users ({isFetching ? "..." : usersData?.count ?? 0})
            </h2>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader className="bg-gray-50/80">
                <TableRow className="hover:bg-transparent">
                  <TableHead className="py-4 w-16 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">No</TableHead>
                  <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">User</TableHead>
                  <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Role</TableHead>
                  <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</TableHead>
                  <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Last Login</TableHead>
                  <TableHead className="py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Join Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading || isFetching ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-12">
                      Loading users...
                    </TableCell>
                  </TableRow>
                ) : !usersData?.results.length ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="text-center py-12 text-gray-500"
                    >
                      No users found matching your filters.
                    </TableCell>
                  </TableRow>
                ) : (
                  usersData.results.map((user, index) => (
                    <TableRow key={user.id} className="hover:bg-gray-50/50 transition-colors group">
                      <TableCell className="font-medium text-gray-600 py-4 w-16 text-center">
                        {(page - 1) * 10 + index + 1}
                      </TableCell>
                      <TableCell className="py-4">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10 ring-2 ring-white shadow-sm">
                            <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-medium">
                              {getInitials(
                                `${user.first_name} ${user.last_name}`
                              )}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium text-gray-900">
                              {user.first_name} {user.last_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {user.email}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="py-4">
                        <Badge
                          variant="secondary"
                          className={
                            user.role === "teacher"
                              ? "bg-indigo-50 text-indigo-700 border border-indigo-200/50 hover:bg-indigo-100 rounded-full px-3 py-0.5 font-medium"
                              : "bg-emerald-50 text-emerald-700 border border-emerald-200/50 hover:bg-emerald-100 rounded-full px-3 py-0.5 font-medium"
                          }
                        >
                          {user.role}
                        </Badge>
                      </TableCell>
                      <TableCell className="py-4">
                        <Badge
                          variant="secondary"
                          className={
                            user.is_banned
                              ? "bg-rose-50 text-rose-700 border border-rose-200/50 hover:bg-rose-100 rounded-full px-3 py-0.5 font-medium"
                              : "bg-teal-50 text-teal-700 border border-teal-200/50 hover:bg-teal-100 rounded-full px-3 py-0.5 font-medium"
                          }
                        >
                          {user.is_banned ? "Banned" : "Active"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-500 py-4">
                        {user.last_login ? formatDate(user.last_login) : "Never"}
                      </TableCell>
                      <TableCell className="text-gray-500 py-4 font-medium">
                        {formatDate(user.date_joined)}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="border-t border-gray-200 px-6 py-4">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() => setPage(Math.max(1, page - 1))}
                      className={
                        page === 1
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>

                  {renderPaginationItems()}

                  <PaginationItem>
                    <PaginationNext
                      onClick={() => setPage(Math.min(totalPages, page + 1))}
                      className={
                        page === totalPages
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
