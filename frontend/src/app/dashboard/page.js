"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FiBriefcase,
  FiCheckCircle,
  FiEdit3,
  FiFileText,
  FiPlus,
} from "react-icons/fi";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

const statCards = [
  { label: "Total Jobs", key: "total_jobs", icon: FiFileText },
  { label: "Drafts Created", key: "drafts", icon: FiEdit3 },
  { label: "In Review", key: "review_jobs", icon: FiBriefcase },
  { label: "Published", key: "published_jobs", icon: FiCheckCircle },
];

const pipelineColors = {
  Intake: "bg-[#172554] text-[#c7d2fe] border border-[#334155]",
  Context: "bg-[#1e1b4b] text-[#ddd6fe] border border-[#334155]",
  Draft: "bg-[#3f2b1f] text-[#fed7aa] border border-[#4b5563]",
  Refine: "bg-[#3b1f1f] text-[#fecaca] border border-[#4b5563]",
  Review: "bg-[#052e2b] text-[#a7f3d0] border border-[#334155]",
  Publish: "bg-[#022c22] text-[#a7f3d0] border border-[#334155]",
};

const statusLabels = {
  context_preparation: "Preparing Context",
  revision_requested: "Revision Requested",
  publish_ready: "Ready to Publish",
};

const statusColors = {
  intake: "bg-[#172554] text-[#c7d2fe]",
  context_preparation: "bg-[#1e1b4b] text-[#ddd6fe]",
  review: "bg-[#312e81] text-[#c7d2fe]",
  revision_requested: "bg-[#7c2d12]/30 text-[#fdba74]",
  approved: "bg-[#14532d]/30 text-[#86efac]",
  publish_ready: "bg-[#14532d]/30 text-[#86efac]",
  published: "bg-[#14532d]/30 text-[#86efac]",
  failed: "bg-[#7f1d1d]/25 text-[#fca5a5]",
  rejected: "bg-[#7f1d1d]/25 text-[#fca5a5]",
  refining: "bg-[#1e3a8a]/25 text-[#bfdbfe]",
};

function StatusPill({ status = "unknown" }) {
  const label = statusLabels[status] || status.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusColors[status] || "bg-[#374151] text-slate-200"}`}>{label}</span>;
}

function relativeTime(value) {
  if (!value) return "—";
  const seconds = Math.round((new Date(value).getTime() - Date.now()) / 1000);
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  if (Math.abs(seconds) < 60) return formatter.format(seconds, "second");
  if (Math.abs(seconds) < 3600) return formatter.format(Math.round(seconds / 60), "minute");
  if (Math.abs(seconds) < 86400) return formatter.format(Math.round(seconds / 3600), "hour");
  return formatter.format(Math.round(seconds / 86400), "day");
}

export default function DashboardPage() {
  const { user, userProfile } = useAuth();
  const [dashboard, setDashboard] = useState(null);
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
        if (!response.ok) throw new Error(data.detail || "Unable to load dashboard data.");
        if (active) setDashboard(data);
      } catch (err) {
        if (active) setError(err.message || "Unable to load dashboard data.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [user]);

  const jobs = dashboard?.recent_jobs || [];
  const pipeline = dashboard?.pipeline || [];
  const displayName = userProfile?.displayName || userProfile?.name || user?.displayName || user?.email?.split("@")[0] || "there";

  return (
    <AppLayout initialSelectedNav="Dashboard">
      <div className="flex h-full flex-col overflow-hidden px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8">
        <div className="flex h-full min-h-0 flex-col overflow-hidden">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <h1 className="text-2xl font-semibold tracking-[-0.04em] text-slate-100 sm:text-3xl md:text-[2.1rem]">
              Welcome back, {displayName} <span aria-label="wave">👋</span>
            </h1>
            <Link href="/create-content" className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#f97316] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_10px_18px_rgba(249,115,22,0.25)] transition hover:bg-[#ea580c] sm:px-5 sm:py-3 sm:text-base">
              <FiPlus className="h-4 w-4" />
              New Content Job
            </Link>
          </div>

          {error && <p role="alert" className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</p>}

          <div className="mt-6 grid gap-3 sm:grid-cols-2 sm:gap-4 xl:grid-cols-4">
            {statCards.map(({ label, key, icon: Icon }) => (
              <div key={label} className="rounded-2xl border border-[#2d3748] bg-[#111827] p-3 shadow-[0_1px_0_rgba(15,23,42,0.2)] sm:p-4">
                <div className="flex items-center justify-between">
                  <div className="text-[2rem] font-semibold tracking-[-0.05em] text-slate-100">{loading ? "—" : dashboard?.[key] ?? 0}</div>
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-[#374151] bg-[#182335] text-[#fbbf24] shadow-sm"><Icon className="h-5 w-5" /></div>
                </div>
                <div className="mt-3 text-[1.05rem] font-medium text-slate-300">{label}</div>
              </div>
            ))}
          </div>

          <div className="mt-8 grid flex-1 gap-6 overflow-hidden">
            <section className="overflow-hidden rounded-2xl border border-[#2d3748] bg-[#111827] p-3 shadow-[0_2px_8px_rgba(2,6,23,0.35)] sm:p-4 md:p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold tracking-[-0.04em] text-slate-100 sm:text-[1.5rem] md:text-[1.8rem]">Recent Jobs</h2>
                <Link href="/my-jobs" className="text-xs font-medium text-[#fbbf24] hover:text-[#f59e0b] sm:text-sm">View all →</Link>
              </div>
              <div className="h-full overflow-x-auto rounded-xl border border-[#2d3748] bg-[#0f172a]">
                <div className="grid min-w-[640px] grid-cols-[1.7fr_1rem_0.9fr_0.8fr_0.7fr] items-center gap-4 border-b border-[#2d3748] bg-[#111827] px-4 py-3 text-sm font-medium text-slate-300">
                  <span>Title</span><span>Type</span><span>Status</span><span>Updated</span><span>Owner</span>
                </div>
                {jobs.map((job) => (
                  <div key={job.id} className="grid min-w-[640px] grid-cols-[1.7fr_1rem_0.9fr_0.8fr_0.7fr] items-center gap-4 border-b border-[#1f2937] px-4 py-4 text-sm last:border-b-0">
                    <div className="font-medium text-slate-100">{job.title}</div>
                    <div className="text-slate-300">{job.content_type}</div>
                    <div><StatusPill status={job.status} /></div>
                    <div className="text-slate-400">{relativeTime(job.updated_at)}</div>
                    <div className="text-slate-300">{job.owner}</div>
                  </div>
                ))}
                {!loading && jobs.length === 0 && <p className="px-4 py-10 text-center text-sm text-slate-400">{error ? "Dashboard jobs could not be loaded." : "No content jobs yet. Create a job to get started."}</p>}
              </div>
            </section>
          </div>

          <div className="mt-8 overflow-hidden xl:flex-none">
            <section className="rounded-2xl border border-[#2d3748] bg-[#111827] p-3 shadow-[0_2px_8px_rgba(2,6,23,0.35)] sm:p-4 md:p-5">
              <h2 className="text-xl font-semibold tracking-[-0.04em] text-slate-100 sm:text-[1.5rem] md:text-[1.9rem]">Content Pipeline</h2>
              <div className="mt-5 overflow-x-auto pb-1">
                <div className="grid min-w-0 gap-3 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
                  {pipeline.map(({ name, value }) => (
                    <div key={name} className={`rounded-xl p-3 ${pipelineColors[name] || "bg-[#1e293b] text-slate-200 border border-[#334155]"}`}>
                      <div className="text-sm font-medium">{name}</div>
                      <div className="mt-5 text-[2rem] font-semibold tracking-[-0.05em]">{value}</div>
                    </div>
                  ))}
                  {!loading && pipeline.length === 0 && <p className="text-sm text-slate-400">No pipeline data yet.</p>}
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
