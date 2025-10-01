import { statCards } from '@/data/StatCardData'
import React from 'react'
import StatCard from '../ui/StatChard'

function Support() {
  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {statCards.map((card, index) => (
          <StatCard key={index} {...card} />
        ))}
      </div>
    </div>
  )
}

export default Support
