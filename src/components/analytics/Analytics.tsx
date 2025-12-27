"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, LayoutGrid, UserCheck } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Activity, Trophy } from "lucide-react";

import { useGetAnalyticsQuery } from "@/store/slices/api/analyticsApiSlice";
import PlatformLineChart from "@/components/analytics/PlatformLineChart";
import EngagementTable from "@/components/analytics/EngagementTable";
import StatCard from "../ui/StatChard";

function Analytics() {
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedYear, setSelectedYear] = useState<number | undefined>(
    undefined
  );
  const [tablePage, setTablePage] = useState(1);

  const { data: analytics, isLoading } = useGetAnalyticsQuery({
    year: selectedYear,
    page: tablePage,
  });

  const summary = analytics?.summary;
  const availableYears = analytics?.available_years || [];
  const currentYear = analytics?.selected_year || new Date().getFullYear();

  // Auto-select first available year if none selected
  useEffect(() => {
    if (!selectedYear && availableYears.length > 0) {
      setSelectedYear(currentYear);
    }
  }, [availableYears, currentYear, selectedYear]);

  if (isLoading) {
    return <div className="p-6 text-center">Loading analytics...</div>;
  }

  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="space-y-5">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          <StatCard
            title="Total Users"
            value={summary?.total_users || 0}
            icon={Users}
            iconColor="#3b82f6"
            iconBg="#dbeafe"
          />

          <StatCard
            title="Active Users"
            value={summary?.active_users || 0}
            icon={UserCheck}
            iconColor="#10b981"
            iconBg="#d1fae5"
          />

          <StatCard
            title="Total Challenges"
            value={summary?.total_challenges || 0}
            icon={Trophy}
            iconColor="#8b5cf6"
            iconBg="#e9d5ff"
          />
        </div>

        {/* Tabs Section */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="pt-2 h-auto border-b border-gray-200 bg-white w-full rounded-none justify-start">
            <TabsTrigger
              value="overview"
              className="max-w-32 data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md px-4 py-2.5 data-[state=active]:shadow-none"
            >
              <TrendingUp className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger
              value="engagement"
              className="max-w-32 data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md px-4 py-2.5 data-[state=active]:shadow-none ml-2"
            >
              <LayoutGrid className="mr-2 h-4 w-4" />
              Engagement
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm md:text-lg font-medium">
                Platform Usage Analytics
              </h2>
              <Select
                value={selectedYear?.toString() || ""}
                onValueChange={(v) => {
                  setSelectedYear(v ? Number(v) : undefined);
                  setTablePage(1);
                }}
              >
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Select Year" />
                </SelectTrigger>
                <SelectContent>
                  {availableYears.map((year) => (
                    <SelectItem key={year} value={year.toString()}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <PlatformLineChart
              usageAnalytics={analytics?.usage_analytics || []}
              selectedYear={analytics?.selected_year || currentYear}
            />
          </TabsContent>

          {/* Engagement Tab */}
          <TabsContent value="engagement" className="mt-6">
            <EngagementTable
              engagementData={
                analytics?.student_engagement || {
                  count: 0,
                  results: [],
                  next: null,
                  previous: null,
                }
              }
              currentPage={tablePage}
              onPageChange={(page) => {
                setTablePage(page);
                // Scroll to top of table when changing page
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default Analytics;
