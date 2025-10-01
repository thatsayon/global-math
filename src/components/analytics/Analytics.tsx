"use client";
import React, { useState } from "react";
import {
  Users,
  UserCheck,
  MessageSquare,
  Trophy,
  LayoutGrid,
  TrendingUp,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import PlatformLineChart from "./PlatformLineChart";
import EngagementTable from "./EngagementTable";
import StatCard, { StatCardProps } from "../ui/StatChard";
import { statCards } from "@/data/StatCardData";



const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [timeRange, setTimeRange] = useState("2025");

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) =>
    (currentYear - i).toString()
  );

  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="space-y-5">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {statCards.map((card, index) => (
            <StatCard key={index} {...card} />
          ))}
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

          <TabsContent value="overview" className="">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm md:text-lg font-medium">
                Platform Usage Analytics
              </h2>
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Select Year" />
                </SelectTrigger>
                <SelectContent>
                  {years.map((year) => (
                    <SelectItem key={year} value={year}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <PlatformLineChart timeRange={timeRange} />
          </TabsContent>

          <TabsContent value="engagement" className="mt-6">
            <EngagementTable />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Analytics;
