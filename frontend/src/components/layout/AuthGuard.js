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
      <div className="flex min-h-screen w-full items-center justify-center bg-[#f7f1eb]">
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-[#f0d7c2] bg-[#fffaf7] p-8 shadow-md">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#f56d2a]/10">
            <div className="h-6 w-6 animate-spin rounded-full border-3 border-[#f56d2a] border-t-transparent" />
          </div>
          <p className="text-base font-semibold text-[#1f2328]">Authenticating...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
