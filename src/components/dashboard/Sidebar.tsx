"use client";
import {
  BarChart3,
  Headphones,
  LogOut,
  Settings,
  Shield,
  Sparkles,
  TrendingUp,
  User,
  Users,
  X,
} from "lucide-react";
import { Button } from "../ui/button";
import Link from "next/link";
import { usePathname } from "next/navigation";

const Sidebar = ({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) => {
  const pathname = usePathname();
  const routes = [
    { name: "Overview", icon: BarChart3, path: "/dashboard" },
    {
      name: "User Management",
      icon: Users,
      path: "/dashboard/user-management",
    },
    { name: "Moderation", icon: Shield, path: "/dashboard/moderation" },
    {
      name: "Analytics and reports",
      icon: BarChart3,
      path: "/dashboard/analytics-reports",
    },   
    {
      name: "AI Question Generator",
      icon: Sparkles,
      path: "/dashboard/ai-question-generator",
    },
    {
      name: "Ranking & Engagement",
      icon: TrendingUp,
      path: "/dashboard/ranking-engagement",
    },
    { name: "Support", icon: Headphones, path: "/dashboard/support" },
    { name: "Settings", icon: Settings, path: "/dashboard/settings" },
  ];

  return (
    <>
      {/* Mobile/Tablet Overlay - Only shows when sidebar is open on small screens */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/15 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed rounded-2xl lg:top-6 lg:relative top-0 left-0 h-screen lg:h-[calc(100vh-6.5rem)]
          bg-white border-r border-gray-200 w-72
          z-50 lg:z-0
          transition-transform duration-300 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 lg:hidden">
            {/* Close button - Only visible on mobile/tablet */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onClose}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <ul className="space-y-1">
              {routes.map((route) => {
                const Icon = route.icon;
                const isActive = pathname === route.path;
                return (
                  <li key={route.path}>
                    <Link
                      href={route.path}
                      onClick={() => onClose()} // Close sidebar on mobile when clicking a link
                      className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                        isActive
                          ? "bg-blue-50 text-blue-600"
                          : "text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="font-medium">{route.name}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
