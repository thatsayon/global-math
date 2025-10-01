import {
  BookOpen,
  GraduationCap,
  LucideUserRoundCheck,
  Shield,
  ShieldCheck,
  User,
  UserCog,
  UserLock,
  UserPlus,
  Users,
  UserStar,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";

const stats = [
  {
    title: "Total Users",
    count: "1,247",
    icon: BookOpen,
    iconColor: "bg-[#3B82F6]",
    textColor: "text-gray-600",
    countColor: "text-[#3B82F6]",
  },
  {
    title: "Students",
    count: "986",
    icon: GraduationCap,
    iconColor: "bg-[#10B981]",
    textColor: "text-gray-600",
    countColor: "text-[#10B981]",
  },
  {
    title: "Teacher",
    count: "234",
    icon: UserStar,
    iconColor: "bg-[#953BF6]",
    textColor: "text-gray-600",
    countColor: "text-[#953BF6]",
  },
  {
    title: "Active users",
    count: "1,198",
    icon: LucideUserRoundCheck,
    iconColor: "bg-[#10B981]",
    textColor: "text-gray-600",
    countColor: "text-[#10B981]",
  },
  {
    title: "Banned Users",
    count: "49",
    icon: UserLock,
    iconColor: "bg-[#EF4444]",
    textColor: "text-gray-600",
    countColor: "text-[#EF4444]",
  },
];

const DashboardContent = () => {
  return (
    <div className="p-4 lg:p-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div
                    className={`size-14 ${stat.iconColor} rounded-lg flex items-center justify-center`}
                  >
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className={`text-2xl font-semibold ${stat.textColor}`}>
                      {stat.title}
                    </p>
                    <p className={`text-2xl font-bold ${stat.countColor}`}>
                      {stat.count}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                title: "New user registered",
                subtitle: "Sarah Johnson • Student",
                time: "2 minutes ago",
                icon: UserPlus,
                color: "text-green-600",
              },
              {
                title: "Role changed",
                subtitle: "Michel Chan • Teacher → Admin",
                time: "2 minutes ago",
                icon: UserCog,
                color: "text-blue-600",
              },
              {
                title: "User banned",
                subtitle: "Alex Smith • Student",
                time: "2 minutes ago",
                icon: UserLock,
                color: "text-red-600",
              },
              {
                title: "Permission updated",
                subtitle: "Emma Wilson • Teacher",
                time: "2 minutes ago",
                icon: ShieldCheck,
                color: "text-purple-600",
              },
            ].map((activity, index) => {
              const Icon = activity.icon;
              return (
                <div
                  key={index}
                  className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
                >
                  <div className="flex items-center space-x-4">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center `}
                    >
                      <Icon className={`size-6 ${activity.color}`} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">
                        {activity.title}
                      </p>
                      <p className="text-sm text-gray-500">
                        {activity.subtitle}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-400">{activity.time}</span>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardContent;
