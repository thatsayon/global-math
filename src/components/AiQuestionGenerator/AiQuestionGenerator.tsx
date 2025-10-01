"use client";
import { statCards } from "@/data/StatCardData";
import React, { useState } from "react";
import StatCard from "../ui/StatChard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { BadgeQuestionMark, CircleCheckBig } from "lucide-react";
import AiQuestion from "./AiQuestion";
import Challenges from "./Challenges";

function AiQuestionGenerator() {
  const [activeTab, setActiveTab] = useState<string>("question");
  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {statCards.map((card, index) => (
          <StatCard key={index} {...card} />
        ))}
      </div>
      <div className="mt-4 md:mt-6 lg:mt-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="pt-2 h-auto border-b border-gray-200 bg-white w-full rounded-none justify-start">
            <TabsTrigger
              value="question"
              className="max-w-44 data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md px-4 py-2.5 data-[state=active]:shadow-none"
            >
              <BadgeQuestionMark className="mr-2 size-5" />
              Question Generate
            </TabsTrigger>
            <TabsTrigger
              value="engagement"
              className="max-w-44 data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md px-4 py-2.5 data-[state=active]:shadow-none ml-2"
            >
              <CircleCheckBig className="mr-2 size-5" />
              Engagement
            </TabsTrigger>
          </TabsList>

          <TabsContent value="question" className="">
            <AiQuestion />
          </TabsContent>
          <TabsContent value="engagement" className="mt-6">
            <Challenges />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default AiQuestionGenerator;
