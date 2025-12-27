"use client";

import {
  GraduationCap,
  UserPlus,
  Users,
  UserLock,
  UserRoundCheck,
  UserStar,
  School,
  Trophy,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"; // <-- ShadCN pagination
import { formatDistanceToNow } from "date-fns";
import { useGetDashboardOverviewQuery } from "@/store/slices/api/dashboardApiSlice";
import { LoadingState } from "../elements/Loading";
import { ErrorState } from "../elements/ErrorFetch";
import { useState } from "react";

const ITEMS_PER_PAGE = 5; // You can change this if needed

const DashboardContent = () => {
  const {
    data: overview,
    isLoading,
    isError,
  } = useGetDashboardOverviewQuery();

  const [currentPage, setCurrentPage] = useState(1);

  const stats = [
    {
      title: "Total Users",
      count: overview?.total_user ?? 0,
      icon: Users,
      iconColor: "bg-[#3B82F6]",
      countColor: "text-[#3B82F6]",
    },
    {
      title: "Students",
      count: overview?.total_student ?? 0,
      icon: GraduationCap,
      iconColor: "bg-[#10B981]",
      countColor: "text-[#10B981]",
    },
    {
      title: "Teacher",
      count: overview?.total_teacher ?? 0,
      icon: UserStar,
      iconColor: "bg-[#953BF6]",
      countColor: "text-[#953BF6]",
    },
    {
      title: "Active users",
      count: overview?.total_active_user ?? 0,
      icon: UserRoundCheck,
      iconColor: "bg-[#10B981]",
      countColor: "text-[#10B981]",
    },
    {
      title: "Banned Users",
      count: overview?.total_banned_user ?? 0,
      icon: UserLock,
      iconColor: "bg-[#EF4444]",
      countColor: "text-[#EF4444]",
    },
  ];

  // Icon mapping based on title
  const getActivityIcon = (title: string) => {
    switch (title) {
      case "New user registered":
        return UserPlus;
      case "New classroom created":
        return School;
      case "New challenge created":
        return Trophy;
      default:
        return UserPlus;
    }
  };

  // Color mapping
  const getActivityColor = (title: string) => {
    switch (title) {
      case "New user registered":
        return "text-green-600";
      case "New classroom created":
        return "text-blue-600";
      case "New challenge created":
        return "text-purple-600";
      default:
        return "text-gray-600";
    }
  };

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    return <ErrorState />;
  }

  const activities = overview?.recent_activities || [];
  const totalPages = Math.ceil(activities.length / ITEMS_PER_PAGE);
  const paginatedActivities = activities.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handlePrevious = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNext = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  return (
    <div className="p-4 lg:p-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div
                    className={`size-14 ${stat.iconColor} rounded-lg flex items-center justify-center`}
                  >
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">{stat.title}</p>
                    <p className={`text-2xl font-bold ${stat.countColor}`}>
                      {stat.count.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity with Pagination */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {paginatedActivities.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No recent activity
              </p>
            ) : (
              paginatedActivities.map((activity) => {
                const Icon = getActivityIcon(activity.title);
                const color = getActivityColor(activity.title);

                return (
                  <div
                    key={activity.id}
                    className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                        <Icon className={`size-6 ${color}`} />
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">
                          {activity.title}
                        </p>
                        <p className="text-sm text-gray-500">
                          {activity.affector_name} •{" "}
                          {activity.user_type.charAt(0).toUpperCase() +
                            activity.user_type.slice(1)}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">
                      {formatDistanceToNow(new Date(activity.created_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                );
              })
            )}
          </div>

          {/* Pagination - Only show if more than one page */}
          {totalPages > 1 && (
            <div className="mt-6">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={handlePrevious}
                      className={
                        currentPage === 1
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>

                  {/* Simple page numbers - adjust if you want more advanced logic */}
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <PaginationItem key={page}>
                        <PaginationLink
                          isActive={currentPage === page}
                          onClick={() => setCurrentPage(page)}
                          className="cursor-pointer"
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    )
                  )}

                  {/* Optional: Ellipsis for many pages */}
                  {/* {totalPages > 5 && <PaginationEllipsis />} */}

                  <PaginationItem>
                    <PaginationNext
                      onClick={handleNext}
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
  );
};

export default DashboardContent;