"use client";

import { useState } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export function AdminLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#F3F4F5]">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="relative flex w-full min-h-[calc(100vh-5rem)]">
            <div className="min-h-[calc(100vh-5rem)]">
                <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            </div>
            <div className="w-full">
                {children}
            </div>
        </main>
    </div>
  );
}