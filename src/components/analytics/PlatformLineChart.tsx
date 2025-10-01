"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { ResponsiveContainer, Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts';

interface ChartDataPoint {
  month: string;
  users: number;
  engagement: number;
  activity: number;
}

// Data organized by year
const chartDataByYear: Record<string, ChartDataPoint[]> = {
  '2025': [
    { month: 'Jan', users: 85, engagement: 90, activity: 95 },
    { month: 'Feb', users: 90, engagement: 95, activity: 100 },
    { month: 'Mar', users: 88, engagement: 92, activity: 97 },
    { month: 'Apr', users: 92, engagement: 96, activity: 99 },
    { month: 'May', users: 95, engagement: 98, activity: 102 },
    { month: 'Jun', users: 100, engagement: 105, activity: 108 },
    { month: 'Jul', users: 105, engagement: 110, activity: 115 },
    { month: 'Aug', users: 110, engagement: 115, activity: 120 },
    { month: 'Sep', users: 108, engagement: 112, activity: 118 },
    { month: 'Oct', users: 112, engagement: 118, activity: 122 },
    { month: 'Nov', users: 115, engagement: 120, activity: 125 },
    { month: 'Dec', users: 120, engagement: 125, activity: 130 },
  ],
  '2024': [
    { month: 'Jan', users: 20, engagement: 30, activity: 70 },
    { month: 'Feb', users: 30, engagement: 35, activity: 75 },
    { month: 'Mar', users: 25, engagement: 30, activity: 50 },
    { month: 'Apr', users: 30, engagement: 35, activity: 45 },
    { month: 'May', users: 40, engagement: 50, activity: 55 },
    { month: 'Jun', users: 50, engagement: 55, activity: 52 },
    { month: 'Jul', users: 70, engagement: 90, activity: 95 },
    { month: 'Aug', users: 80, engagement: 85, activity: 80 },
    { month: 'Sep', users: 60, engagement: 70, activity: 68 },
    { month: 'Oct', users: 50, engagement: 60, activity: 65 },
    { month: 'Nov', users: 40, engagement: 55, activity: 95 },
    { month: 'Dec', users: 50, engagement: 60, activity: 100 },
  ],
};

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

const PlatformLineChart: React.FC<{ timeRange: string }> = ({ timeRange }) => {
  const chartData = chartDataByYear[timeRange];

  // If no data available for selected year
  if (!chartData) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-[200px] md:h-[475px]">
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 mb-2">No Data Available</p>
            <p className="text-sm text-gray-500">
              No data available for the selected year ({timeRange})
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
            <AreaChart data={chartData} className='-ml-10 md:ml-0'>
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