import React from "react";
import StatCard from "../ui/StatChard";
import { statCards } from "@/data/StatCardData";
import ModerationTable from "./ModerationTable";

function Moderation() {
  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {statCards.map((card, index) => (
          <StatCard key={index} {...card} />
        ))}
      </div>
      <div className="mt-6 md:mt-8 lg:mt-10 xl:mt-12">
        <ModerationTable/>
      </div>
    </div>
  );
}

export default Moderation;
