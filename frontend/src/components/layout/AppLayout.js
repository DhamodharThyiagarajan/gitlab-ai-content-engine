"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthGuard from "./AuthGuard";
import { useAuth } from "@/hooks/useAuth";
import AppHeader from "./AppHeader";
import SidebarNav, { defaultNavItems } from "./SidebarNav";

export default function AppLayout({ children, initialSelectedNav = "Dashboard" }) {
  const router = useRouter();
  const { userProfile, logout } = useAuth();
  const [selectedNav, setSelectedNav] = useState(initialSelectedNav);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const displayName = userProfile?.displayName || "User";
  const role = (userProfile?.role || "writer").toLowerCase();
  const visibleNavItems = defaultNavItems.filter(({ label }) => {
    if (label === "Create Content") return ["writer", "admin"].includes(role);
    if (label === "Review") return ["reviewer", "approver", "admin"].includes(role);
    if (label === "Analytics") return ["reviewer", "approver", "admin"].includes(role);
    return true;
  });

  const handleNavSelect = ({ label, route }) => {
    setSelectedNav(label);
    setIsMenuOpen(false);

    if (route) {
      router.push(route);
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#070d18] p-3 text-slate-100 sm:p-4 md:p-5 lg:h-[calc(100vh-1.5rem)] lg:p-6">
        <div className="mx-auto flex w-full flex-col overflow-hidden rounded-[18px] border border-[#2d3748] bg-[#111827] shadow-[0_12px_28px_rgba(2,6,23,0.45)] lg:h-[calc(100vh-3rem)] lg:flex-row">
          <aside className="hidden w-[260px] border-r border-[#2d3748] bg-[#0f172a] px-4 py-5 lg:flex lg:flex-col">
            <SidebarNav items={visibleNavItems} selectedNav={selectedNav} onSelect={handleNavSelect} />
          </aside>

          <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-[#0f172a]">
            <AppHeader
              onMenuToggle={() => setIsMenuOpen((prev) => !prev)}
              userName={displayName}
              onLogout={logout}
            />

            {isMenuOpen && (
              <div className="border-b border-[#2d3748] bg-[#0f172a] px-3 py-3 lg:hidden">
                <SidebarNav
                  items={visibleNavItems}
                  selectedNav={selectedNav}
                  onSelect={handleNavSelect}
                  isMobile
                />
              </div>
            )}

            <div className="h-full min-h-0 overflow-y-auto overflow-x-hidden">{children}</div>
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
