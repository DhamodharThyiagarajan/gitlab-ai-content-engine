"use client";

import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthGuard({ children }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen w-full items-center justify-center bg-[#070d18]">
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-[#2d3748] bg-[#111827] p-8 shadow-[0_10px_30px_rgba(2,6,23,0.45)]">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#f97316]/10">
            <div className="h-6 w-6 animate-spin rounded-full border-3 border-[#f97316] border-t-transparent" />
          </div>
          <p className="text-base font-semibold text-slate-100">Authenticating...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
