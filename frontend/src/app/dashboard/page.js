"use client";

import {
  FiBriefcase,
  FiCheckCircle,
  FiEdit3,
  FiFileText,
  FiHome,
  FiLayers,
  FiPlus,
  FiUpload,
} from "react-icons/fi";
import AppLayout from "@/components/layout/AppLayout";

const stats = [
  { label: "Total Jobs", value: 24, icon: FiFileText },
  { label: "Drafts Created", value: 16, icon: FiEdit3 },
  { label: "In Review", value: 6, icon: FiBriefcase },
  { label: "Published", value: 12, icon: FiCheckCircle },
];

const jobs = [
  { title: "v16.8 Release Notes", type: "Release Notes", status: "In Review", updated: "2 hours ago", owner: "Dhamo" },
  { title: "New CI/CD Pipeline Feature", type: "Documentation", status: "Drafting", updated: "5 hours ago", owner: "Dhamo" },
  { title: "API: Merge Request Endpoints", type: "API Reference", status: "Review Needed", updated: "1 day ago", owner: "Dhamo" },
  { title: "Onboarding: Self-Hosted Setup", type: "Guide", status: "Published", updated: "2 days ago", owner: "Dhamo" },
  { title: "GitLab Duo Blog", type: "Blog", status: "Tone Optimization", updated: "3 days ago", owner: "Dhamo" },
];

const pipeline = [
  { name: "Intake", value: 8, color: "bg-[#eaf1ff] text-[#486ad7]" },
  { name: "Context", value: 6, color: "bg-[#f7f3ff] text-[#7a5dd7]" },
  { name: "Draft", value: 7, color: "bg-[#fff4eb] text-[#d4882b]" },
  { name: "Refine", value: 5, color: "bg-[#fff1f0] text-[#d66b57]" },
  { name: "Review", value: 6, color: "bg-[#e9f9f2] text-[#2d8c68]" },
  { name: "Publish", value: 12, color: "bg-[#eafaf1] text-[#2c9d6a]" },
];

const quickActions = [
  { label: "Create from MR", icon: FiFileText },
  { label: "Upload Documents", icon: FiUpload },
  { label: "Use Template", icon: FiLayers },
  { label: "Explore Examples", icon: FiHome },
];



function StatusPill({ status }) {
  const tone = {
    "In Review": "bg-[#f0ecff] text-[#5c4ac8]",
    Drafting: "bg-[#edf3ff] text-[#3d6ad8]",
    "Review Needed": "bg-[#fff0e5] text-[#d78a2b]",
    Published: "bg-[#eafaf0] text-[#2b9d68]",
    "Tone Optimization": "bg-[#edf5ff] text-[#4c76d8]",
  };

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${tone[status] || "bg-[#edf2f7] text-[#49505a]"}`}>
      {status}
    </span>
  );
}

export default function DashboardPage() {
  return (
    <AppLayout initialSelectedNav="Dashboard">
      <div className="flex h-full flex-col overflow-hidden px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8">
        <div className="flex h-full min-h-0 flex-col overflow-hidden">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <h1 className="text-2xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-3xl md:text-[2.1rem]">
              Welcome back, Dhamo <span aria-label="wave">👋</span>
            </h1>

            <button
              type="button"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#f56d2a] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_10px_18px_rgba(245,109,42,0.22)] transition hover:bg-[#e55f1c] sm:px-5 sm:py-3 sm:text-base"
            >
              <FiPlus className="h-4 w-4" />
              New Content Job
            </button>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 sm:gap-4 xl:grid-cols-4">
            {stats.map(({ label, value, icon: Icon }) => (
              <div key={label} className="rounded-2xl border border-[#f0dfd1] bg-[#fffaf7] p-3 shadow-[0_1px_0_rgba(15,23,42,0.02)] sm:p-4">
                <div className="flex items-center justify-between">
                  <div className="text-[2rem] font-semibold tracking-[-0.05em] text-[#232933]">{value}</div>
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-[#f2d8c4] bg-[#fff4ee] text-[#d8662f] shadow-sm">
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
                <div className="mt-3 text-[1.05rem] font-medium text-[#3d434d]">{label}</div>
              </div>
            ))}
          </div>

          <div className="mt-8 grid flex-1 gap-6 overflow-hidden xl:grid-cols-[minmax(0,1.8fr)_minmax(260px,0.9fr)]">
            <section className="overflow-hidden rounded-2xl border border-[#f2dfd2] bg-[#fffaf7] p-3 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-4 md:p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[1.5rem] md:text-[1.8rem]">Recent Jobs</h2>
                <button type="button" className="text-xs font-medium text-[#d85c2a] hover:text-[#bf4d1e] sm:text-sm">
                  View all →
                </button>
              </div>

              <div className="h-full overflow-x-auto rounded-xl border border-[#f1dfd2] bg-white">
                <div className="grid min-w-[640px] grid-cols-[1.7fr_1rem_0.9fr_0.8fr_0.7fr] items-center gap-4 border-b border-[#f3dfd2] bg-[#fff6f2] px-4 py-3 text-sm font-medium text-[#6b564b]">
                  <span>Title</span>
                  <span>Type</span>
                  <span>Status</span>
                  <span>Updated</span>
                  <span>Owner</span>
                </div>

                {jobs.map((job) => (
                  <div key={job.title} className="grid min-w-[640px] grid-cols-[1.7fr_1rem_0.9fr_0.8fr_0.7fr] items-center gap-4 border-b border-[#edf1f4] px-4 py-4 text-sm last:border-b-0">
                    <div className="font-medium text-[#2d3340]">{job.title}</div>
                    <div className="text-[#4d5561]">{job.type}</div>
                    <div>
                      <StatusPill status={job.status} />
                    </div>
                    <div className="text-[#5f6875]">{job.updated}</div>
                    <div className="flex items-center justify-between text-[#49515c]">
                      <span>{job.owner}</span>
                      <button type="button" className="text-lg text-[#8d6254] hover:text-[#4d352c]">•••</button>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <aside className="rounded-2xl border border-[#f2dfd2] bg-[#fffaf7] p-3 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-4 md:p-5">
              <h2 className="text-xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[1.5rem] md:text-[1.9rem]">Quick Actions</h2>
              <div className="mt-5 grid grid-cols-2 gap-3">
                {quickActions.map(({ label, icon: Icon }) => (
                  <button
                    key={label}
                    type="button"
                    className="flex min-h-[88px] flex-col items-center justify-center gap-2 rounded-xl border border-[#f2d9c8] bg-white text-center text-xs font-medium text-[#2e3641] shadow-sm transition hover:bg-[#fff4ee] sm:text-sm"
                  >
                    <Icon className="h-5 w-5 text-[#4a5160]" />
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            </aside>
          </div>

          <div className="mt-8 overflow-hidden xl:flex-none">
            <section className="rounded-2xl border border-[#f2dfd2] bg-[#fffaf7] p-3 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-4 md:p-5">
              <h2 className="text-xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[1.5rem] md:text-[1.9rem]">Content Pipeline</h2>
              <div className="mt-5 overflow-x-auto pb-1">
                <div className="grid min-w-0 gap-3 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
                  {pipeline.map(({ name, value, color }) => (
                    <div key={name} className={`rounded-xl border border-[#e7ebf0] p-3 ${color}`}>
                      <div className="text-sm font-medium">{name}</div>
                      <div className="mt-5 text-[2rem] font-semibold tracking-[-0.05em]">{value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
