"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import { getBackendUrl } from "@/lib/backend";

const BACKEND_URL = getBackendUrl();

const statCards = [
  { label: "Total Content Jobs", key: "total_jobs", format: (value) => value },
  { label: "Published", key: "published_jobs", format: (value) => value },
  { label: "Drafts Created", key: "drafts", format: (value) => value },
  { label: "Average Quality", key: "average_quality", format: (value) => `${value}/100` },
];

export default function AnalyticsPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    let active = true;
    (async () => {
      try {
        const token = await user.getIdToken();
        const response = await fetch(`${BACKEND_URL}/api/metrics`, { headers: { Authorization: `Bearer ${token}` } });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || "Unable to load analytics data.");
        if (active) setAnalytics(data);
      } catch (err) {
        if (active) setError(err.message || "Unable to load analytics data.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [user]);

  const trend = analytics?.trend || [];
  const maxJobs = Math.max(0, ...trend.map((month) => month.jobs || 0));

  return (
    <AppLayout initialSelectedNav="Analytics">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#2d3748] bg-[#111827] p-4 shadow-[0_2px_8px_rgba(2,6,23,0.35)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-slate-100 sm:text-[2.1rem]">Analytics</h1>
              <p className="mt-2 text-sm text-slate-400 sm:text-[1rem]">Job volume, publishing progress, and document quality from your database.</p>
            </div>
            <div className="rounded-xl border border-[#374151] bg-[#0f172a] px-4 py-2.5 text-sm text-slate-300">Last 7 months</div>
          </div>

          {error && <p role="alert" className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</p>}

          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {statCards.map(({ label, key, format }) => (
              <div key={label} className="rounded-[20px] border border-[#2d3748] bg-[#0f172a] p-4">
                <div className="text-sm text-slate-400">{label}</div>
                <div className="mt-3 text-[2rem] font-semibold tracking-[-0.05em] text-slate-100">{loading ? "—" : format(analytics?.[key] ?? 0)}</div>
                <div className="mt-2 text-xs text-slate-500">Live database value</div>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-[20px] border border-[#2d3748] bg-[#0f172a] p-4 sm:p-5">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div><h2 className="text-lg font-semibold text-slate-100">Content Trend</h2><p className="mt-1 text-sm text-slate-400">Jobs created per month</p></div>
              <span className="flex items-center gap-2 text-xs text-slate-400"><span className="h-2.5 w-2.5 rounded-sm bg-gradient-to-t from-[#f97316] to-[#fbbf24]" />Jobs</span>
            </div>
            {trend.length > 0 ? <div className="grid h-56 grid-cols-7 items-end gap-2 border-b border-[#334155] px-1 sm:gap-4">
              {trend.map((month, index) => {
                const value = month.jobs || 0;
                const height = maxJobs ? Math.max(value ? 8 : 0, (value / maxJobs) * 100) : 0;
                return <div key={`${month.month}-${index}`} className="flex h-full min-w-0 flex-col items-center justify-end gap-2" title={`${month.month}: ${value} jobs`}>
                  <span className="text-xs text-slate-400">{value}</span>
                  <div className="w-full max-w-12 rounded-t-lg bg-gradient-to-t from-[#f97316] to-[#fbbf24] transition-all" style={{ height: `${height}%` }} />
                  <span className="pb-2 text-xs text-slate-400">{month.month}</span>
                </div>;
              })}
            </div> : <div className="flex h-44 items-center justify-center text-sm text-slate-400">{loading ? "Loading trend…" : "No job history for this period."}</div>}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
