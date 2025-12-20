// components/moderation/Moderation.tsx
"use client";

import { useGetModerationDataQuery } from "@/store/slices/api/moderationApiSlice";
import StatCard from "../ui/StatChard";
import ModerationTable from "./ModerationTable";
import { Users, UserCheck, FileText, Trophy } from "lucide-react";
import { LoadingState } from "../elements/Loading";

function Moderation() {
  const { data, isLoading } = useGetModerationDataQuery({});

  const stats = [
    {
      title: "Total Users",
      value: data?.top.total_user || 0,
      icon: Users,
      iconColor: "#3b82f6",
      iconBg: "#dbeafe",
    },
    {
      title: "Active Users",
      value: data?.top.total_active_user || 0,
      icon: UserCheck,
      iconColor: "#10b981",
      iconBg: "#d1fae5",
    },
    {
      title: "Total Posts",
      value: data?.top.total_post || 0,
      icon: FileText,
      iconColor: "#8b5cf6",
      iconBg: "#ede9fe",
    },
    {
      title: "Challenges",
      value: data?.top.total_challenge || 0,
      icon: Trophy,
      iconColor: "#f59e0b",
      iconBg: "#fffbeb",
    },
  ];
if(isLoading) return <LoadingState/>
  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
        {stats.map((stat, i) => (
          <StatCard key={i} {...stat} />
        ))}
      </div>

      <ModerationTable />
    </div>
  );
}

export default Moderation;