"use client";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";
import { Button } from "../ui/button";
import ProfileDropdown from "./ProfileDropdown";
import Logo from "../elements/Logo";

const Navbar = ({ onMenuClick }: { onMenuClick?: () => void }) => {
  const pathname = usePathname();

  // Split the path
  const parts = pathname.split("/").filter(Boolean);

  // Define titles for specific routes
  const getPageTitle = (path: string) => {
    const routes: { [key: string]: string } = {
      dashboard: "Dashboard Overview",
      "user-management": "User Management",
      moderation: "Moderation",
      "analytics-reports": "Analytics and Reports",
      profile: "Profile",
      "ai-question-generator": "AI Question Generator",
      "ranking-engagement": "Ranking & Engagement",
      support: "Support",
      settings: "Settings",
    };

    // last part of the path (eg. "profile")
    const last = parts[parts.length - 1];
    return routes[last] || "Dashboard";
  };

  return (
    <nav className="bg-white lg:px-6 sticky top-0 z-30">
      <div className="flex items-center justify-between h-20 px-4 lg:px-0">
        {/* Left side - Menu button and title */}
        <div className="flex items-center gap-2">
          {onMenuClick && (
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onMenuClick}
            >
              <Menu className="size-6" />
            </Button>
          )}
          <Logo />
        </div>
        <div className="flex items-center justify-between space-x-4">
          {/* Mobile Menu Button - Only visible on mobile/tablet */}

          <h1 className="text-3xl font-semibold text-gray-800 hidden sm:block">
            {getPageTitle(pathname)}
          </h1>

          {/* Right side - Profile */}
        </div>
        <ProfileDropdown />
      </div>
    </nav>
  );
};

export default Navbar;
