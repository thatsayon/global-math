"use client"
import React from "react";
import StatCard from "../ui/StatChard";
import RankingTable from "./RankingTable";
import { useGetTopCardInfoQuery } from "@/store/slices/api/ApiSlice";
import { LoadingState } from "../elements/Loading";
import { Trophy, UserCheck, Users } from "lucide-react";

function Ranking() {
  const { data, isLoading } = useGetTopCardInfoQuery();

  if (isLoading) return <LoadingState />;
  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <StatCard
          title="Total Users"
          value={data?.total_users || 0}
          icon={Users}
          iconColor="#3b82f6"
          iconBg="#dbeafe"
        />

        <StatCard
          title="Active Users"
          value={data?.active_users || 0}
          icon={UserCheck}
          iconColor="#10b981"
          iconBg="#d1fae5"
        />

        <StatCard
          title="Total Challenges"
          value={data?.total_challenges || 0}
          icon={Trophy}
          iconColor="#8b5cf6"
          iconBg="#e9d5ff"
        />
      </div>
      <div>
        <RankingTable />
      </div>
    </div>
  );
}

export default Ranking;
