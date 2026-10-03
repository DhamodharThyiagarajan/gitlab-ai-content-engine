"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import AppLayout from "@/components/layout/AppLayout";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import { useAuth } from "@/hooks/useAuth";

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");
const filters = ["All", "In Progress", "Completed", "Failed"];

const statusLabels = {
  intake: "Intake",
  context_preparation: "Preparing Context",
  review: "In Review",
  revision_requested: "Revision Requested",
  refining: "Refining",
  approved: "Approved",
  publish_ready: "Ready to Publish",
  published: "Published",
  failed: "Failed",
  rejected: "Rejected",
};

const statusStyles = {
  published: "bg-[#14532d]/25 text-[#86efac]",
  approved: "bg-[#14532d]/25 text-[#86efac]",
  publish_ready: "bg-[#14532d]/25 text-[#86efac]",
  intake: "bg-[#7c2d12]/30 text-[#fdba74]",
  context_preparation: "bg-[#1d4ed8]/20 text-[#bfdbfe]",
  review: "bg-[#1d4ed8]/20 text-[#bfdbfe]",
  revision_requested: "bg-[#7c2d12]/30 text-[#fdba74]",
  refining: "bg-[#1d4ed8]/20 text-[#bfdbfe]",
  failed: "bg-[#7f1d1d]/25 text-[#fca5a5]",
  rejected: "bg-[#7f1d1d]/25 text-[#fca5a5]",
};

function jobCategory(status) {
  if (status === "published") return "Completed";
  if (["failed", "rejected"].includes(status)) return "Failed";
  return "In Progress";
}

function formatStatus(status) {
  return statusLabels[status] || status.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
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

function StatusBadge({ status }) {
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusStyles[status] || "bg-[#374151] text-slate-200"}`}>{formatStatus(status)}</span>;
}

export default function MyJobsPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    let active = true;
    (async () => {
      try {
        const token = await user.getIdToken();
        const response = await fetch(`${BACKEND_URL}/api/content-jobs`, { headers: { Authorization: `Bearer ${token}` } });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || "Unable to load content jobs.");
        if (active) setJobs(Array.isArray(data) ? data : []);
      } catch (err) {
        if (active) setError(err.message || "Unable to load content jobs.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [user]);

  const filteredJobs = useMemo(() => selectedFilter === "All" ? jobs : jobs.filter((job) => jobCategory(job.status) === selectedFilter), [jobs, selectedFilter]);

  const openJob = async (jobId) => {
    if (!user) return;
    setDetailLoading(true);
    setSelectedJob(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${BACKEND_URL}/api/content-jobs/${jobId}`, { headers: { Authorization: `Bearer ${token}` } });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Unable to load this job.");
      setSelectedJob(data);
    } catch (err) {
      setError(err.message || "Unable to load this job.");
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <AppLayout initialSelectedNav="My Jobs">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#2d3748] bg-[#111827] p-4 shadow-[0_2px_8px_rgba(2,6,23,0.35)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-slate-100 sm:text-[2.1rem]">My Jobs</h1>
              <p className="mt-2 text-sm text-slate-400 sm:text-[1rem]">Manage your content workflow and monitor each job status.</p>
            </div>
            <Link href="/create-content" className="inline-flex items-center justify-center rounded-xl bg-[#f97316] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#ea580c]">New Content Job</Link>
          </div>

          {error && <p role="alert" className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</p>}

          <div className="mt-6 flex flex-wrap gap-2" role="group" aria-label="Filter jobs by status">
            {filters.map((filter) => (
              <button key={filter} type="button" onClick={() => setSelectedFilter(filter)} aria-pressed={selectedFilter === filter} className={`rounded-xl px-3 py-2 text-sm font-medium transition ${selectedFilter === filter ? "bg-[#f97316] text-white shadow-[0_8px_18px_rgba(249,115,22,0.2)]" : "border border-[#374151] bg-[#0f172a] text-slate-300 hover:bg-[#182335]"}`}>
                {filter} <span className="ml-1 opacity-70">{filter === "All" ? jobs.length : jobs.filter((job) => jobCategory(job.status) === filter).length}</span>
              </button>
            ))}
          </div>

          <div className="mt-6 overflow-x-auto rounded-[20px] border border-[#2d3748] bg-[#0f172a]">
            <div className="grid min-w-[700px] grid-cols-[1.6fr_0.9fr_0.9fr_0.9fr_0.6fr] gap-4 border-b border-[#2d3748] bg-[#111827] px-4 py-3 text-sm font-medium text-slate-300">
              <span>Title</span><span>Type</span><span>Status</span><span>Updated</span><span>Actions</span>
            </div>
            {filteredJobs.map((job) => (
              <div key={job.id} className="grid min-w-[700px] grid-cols-[1.6fr_0.9fr_0.9fr_0.9fr_0.6fr] items-center gap-4 border-b border-[#1f2937] px-4 py-4 text-sm last:border-b-0">
                <div className="font-medium text-slate-100">{job.title}</div>
                <div className="text-slate-300">{job.content_type}</div>
                <div><StatusBadge status={job.status} /></div>
                <div className="text-slate-400">{relativeTime(job.updated_at || job.created_at)}</div>
                <button type="button" onClick={() => openJob(job.id)} className="text-left text-[#fbbf24] hover:text-[#f59e0b]">View</button>
              </div>
            ))}
            {!loading && filteredJobs.length === 0 && <p className="px-4 py-10 text-center text-sm text-slate-400">{error ? "Jobs could not be loaded." : jobs.length ? `No ${selectedFilter.toLowerCase()} jobs.` : "No jobs yet. Create a content job to get started."}</p>}
            {loading && <p className="px-4 py-10 text-center text-sm text-slate-400">Loading jobs…</p>}
          </div>
        </div>
      </div>
      {(detailLoading || selectedJob) && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-3 sm:p-6" role="dialog" aria-modal="true" aria-label="Job details">
        <div className="flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-[#374151] bg-[#111827] shadow-2xl">
          <header className="flex items-start justify-between gap-4 border-b border-[#2d3748] px-5 py-4">
            <div><p className="text-xs uppercase tracking-wider text-slate-500">Job details</p><h2 className="mt-1 text-xl font-semibold text-slate-100">{selectedJob?.title || "Loading job…"}</h2></div>
            <button type="button" onClick={() => setSelectedJob(null)} className="rounded-lg border border-[#374151] px-3 py-1.5 text-sm text-slate-300 hover:bg-[#182335]">Close</button>
          </header>
          {detailLoading ? <p className="p-8 text-center text-sm text-slate-400">Loading job details…</p> : selectedJob && <div className="overflow-y-auto p-5">
            <div className="mb-5 flex flex-wrap items-center gap-3 text-sm text-slate-400"><StatusBadge status={selectedJob.status} /><span>{selectedJob.content_type}</span><span>{selectedJob.audience}</span><span>Quality score: {selectedJob.quality_score ?? "—"}</span></div>
            {selectedJob.final_document ? <MarkdownRenderer content={selectedJob.final_document} /> : <><h3 className="mb-2 text-sm font-semibold text-slate-200">Source document text</h3><pre className="whitespace-pre-wrap break-words rounded-xl border border-[#2d3748] bg-[#0f172a] p-4 text-sm leading-6 text-slate-300">{selectedJob.source_text || "No source text is available."}</pre></>}
          </div>}
        </div>
      </div>}
    </AppLayout>
  );
}
