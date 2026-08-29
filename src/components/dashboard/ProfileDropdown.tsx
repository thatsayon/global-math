"use client";

import { LogOut, User } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Button } from "../ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../ui/dropdown-menu";
import Link from "next/link";
import { useGetProfileQuery } from "@/store/slices/api/profileApiSlice";
import { removeCookie } from "@/hooks/cookie";
import { useState } from "react";
import { toast } from "sonner";

// The login screen is served from the app root, not /login
const LOGIN_PATH = "/";

const ProfileDropdown = () => {
  const { data: profile } = useGetProfileQuery();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const getInitials = () => {
    if (!profile) return "U";
    return `${profile.first_name?.[0] || ""}${profile.last_name?.[0] || ""}`.toUpperCase() || "U";
  };

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);

    try {
      const res = await fetch("/api/logout", { method: "POST" });
      if (!res.ok) throw new Error("Logout request failed");
    } catch (err) {
      console.error("Logout failed:", err);
      toast.error("Could not reach the server, signing out locally");
      // Fall back to clearing the cookies from the browser
      removeCookie("access");
      removeCookie("refresh");
    }

    // Hard navigation so the cached RTK Query / Redux state is dropped too
    window.location.replace(LOGIN_PATH);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-10 w-10 rounded-full ring-2 ring-white shadow-sm overflow-hidden p-0">
          <Avatar className="h-10 w-10">
            <AvatarImage
              src={profile?.profile_pic || ""}
              alt="Profile"
              className="object-cover"
            />
            <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-medium">
              {getInitials()}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-48" align="end" forceMount>
        <DropdownMenuItem asChild>
          <Link href="/dashboard/settings" className="cursor-pointer">
            <User className="mr-2 h-4 w-4" />
            <span>Profile</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={handleLogout}
          disabled={isLoggingOut}
          className="cursor-pointer"
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>{isLoggingOut ? "Logging out..." : "Logout"}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ProfileDropdown;