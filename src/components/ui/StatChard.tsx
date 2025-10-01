import React from 'react';
import { Card } from '@/components/ui/card';

export interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties; strokeWidth?: number }>;
  iconColor?: string;
  iconBg?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  iconColor = '#3b82f6',
  iconBg = '#dbeafe',
}) => {
  return (
    <Card className="w-full p-4 sm:p-5 md:p-6">
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Icon Container */}
        <div
          className="flex items-center justify-center rounded-lg p-2 sm:p-2.5 md:p-3 shrink-0"
          style={{ backgroundColor: iconBg }}
        >
          <Icon
            className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7"
            style={{ color: iconColor }}
            strokeWidth={2}
          />
        </div>

        {/* Content */}
        <div className="flex flex-col min-w-0">
          <h3 className="text-xs sm:text-sm md:text-base text-gray-600 font-medium mb-0.5 sm:mb-1">
            {title}
          </h3>
          <p className="text-2xl sm:text-3xl font-bold text-gray-900 truncate">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
        </div>
      </div>
    </Card>
  );
};

export default StatCard;
