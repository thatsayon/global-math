"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { ResponsiveContainer, Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts';
import { UsageAnalytics } from '@/types/analytics.type';

interface PlatformLineChartProps {
  usageAnalytics: UsageAnalytics[];
  selectedYear: number;
}

const chartConfig = {
  users: {
    label: "Users",
    color: "#60a5fa",
  },
  engagement: {
    label: "Engagement",
    color: "#fb923c",
  },
  activity: {
    label: "Activity",
    color: "#a78bfa",
  },
};

const PlatformLineChart: React.FC<PlatformLineChartProps> = ({ usageAnalytics, selectedYear }) => {
  if (usageAnalytics.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-[200px] md:h-[475px]">
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 mb-2">No Data Available</p>
            <p className="text-sm text-gray-500">
              No analytics data for {selectedYear}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardContent className="pt-6">
        <ChartContainer config={chartConfig} className="h-[200px] md:h-[385px] w-[110%] md:w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={usageAnalytics} className='-ml-10 md:ml-0'>
              <defs>
                <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#a78bfa" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorEngagement" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#fb923c" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#fb923c" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#60a5fa" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Area
                type="monotone"
                dataKey="activity"
                stroke="#a78bfa"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorActivity)"
              />
              <Area
                type="monotone"
                dataKey="engagement"
                stroke="#fb923c"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorEngagement)"
              />
              <Area
                type="monotone"
                dataKey="users"
                stroke="#60a5fa"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorUsers)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default PlatformLineChart;