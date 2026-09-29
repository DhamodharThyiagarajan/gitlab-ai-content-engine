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

  const handleNavSelect = ({ label, route }) => {
    setSelectedNav(label);
    setIsMenuOpen(false);

    if (route) {
      router.push(route);
    }
  };

  return (
    <AuthGuard>
    <div className="min-h-screen bg-[#f7f1eb] p-3 text-[#1f2328] sm:p-4 md:p-5 lg:h-[calc(100vh-1.5rem)] lg:p-6">
      <div className="mx-auto flex w-full flex-col overflow-hidden rounded-[18px] border border-[#f0d7c2] bg-[#fffaf7] shadow-[0_8px_24px_rgba(94,58,32,0.08)] lg:h-[calc(100vh-3rem)] lg:flex-row">
        <aside className="hidden w-[260px] border-r border-[#f3dfd0] bg-[#fff7f3] px-4 py-5 lg:flex lg:flex-col">
          <SidebarNav items={defaultNavItems} selectedNav={selectedNav} onSelect={handleNavSelect} />
        </aside>

        <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-[#fffaf7]">
          <AppHeader
            onMenuToggle={() => setIsMenuOpen((prev) => !prev)}
            userName={displayName}
            onLogout={logout}
          />

          {isMenuOpen && (
            <div className="border-b border-[#f0dfd3] bg-[#fffaf7] px-3 py-3 lg:hidden">
              <SidebarNav
                items={defaultNavItems}
                selectedNav={selectedNav}
                onSelect={handleNavSelect}
                isMobile
              />
            </div>
          )}

          <div className="h-full min-h-0 overflow-hidden">{children}</div>
        </main>
      </div>
    </div>
    </AuthGuard>
  );
}
