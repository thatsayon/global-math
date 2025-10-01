import { StatCardProps } from "@/components/ui/StatChard";
import { MessageSquare, Trophy, UserCheck, Users } from "lucide-react";

export const statCards: StatCardProps[] = [
  {
    title: "Total Users",
    value: "1,247",
    icon: Users,
    iconColor: "#3840D0",
    iconBg: "#DBEAFE",
  },
  {
    title: "Active Users",
    value: "892",
    icon: UserCheck,
    iconColor: "#15803D",
    iconBg: "#DCFCE7",
  },
  {
    title: "Total Posts",
    value: "640",
    icon: MessageSquare,
    iconColor: "#B558EA",
    iconBg: "#F3E8FF",
  },
  {
    title: "Challenges",
    value: "234",
    icon: Trophy,
    iconColor: "#EA580C",
    iconBg: "#FFEDD5",
  },
];