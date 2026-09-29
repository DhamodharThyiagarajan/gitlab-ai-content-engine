"use client";

import AppLayout from "@/components/layout/AppLayout";

const jobs = [
  { title: "API Reference Upgrade", type: "Documentation", status: "Completed", updated: "2 hours ago", owner: "Dhamo" },
  { title: "Release Notes v16.4", type: "Release Notes", status: "In Progress", updated: "5 hours ago", owner: "Dhamo" },
  { title: "User Guide Refresh", type: "Guide", status: "Pending", updated: "1 day ago", owner: "Dhamo" },
  { title: "System Architecture Doc", type: "Documentation", status: "Failed", updated: "2 days ago", owner: "Dhamo" },
  { title: "Product Blog Draft", type: "Blog", status: "Completed", updated: "3 days ago", owner: "Dhamo" },
];

const filters = ["All", "In Progress", "Completed", "Failed"];

function StatusBadge({ status }) {
  const palette = {
    Completed: "bg-[#eafaf0] text-[#2a9d67]",
    "In Progress": "bg-[#edf3ff] text-[#3d6ad8]",
    Pending: "bg-[#fff0e5] text-[#d38b31]",
    Failed: "bg-[#ffe9e6] text-[#d25d4d]",
  };

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${palette[status] || "bg-[#edf2f7] text-[#49505a]"}`}>
      {status}
    </span>
  );
}

export default function MyJobsPage() {
  return (
    <AppLayout initialSelectedNav="My Jobs">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#f0dfd2] bg-[#fffaf7] p-4 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[2.1rem]">My Jobs</h1>
              <p className="mt-2 text-sm text-[#6a6f76] sm:text-[1rem]">
                Manage your content workflow and monitor each job status.
              </p>
            </div>

            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl border border-[#f1d7c3] bg-[#fff5ef] px-4 py-2.5 text-sm font-medium text-[#2e3641] transition hover:bg-[#fef1e8]"
            >
              Filter
            </button>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {filters.map((filter, index) => (
              <button
                key={filter}
                type="button"
                className={`rounded-xl px-3 py-2 text-sm font-medium transition ${
                  index === 0
                    ? "bg-[#f56d2a] text-white shadow-[0_8px_18px_rgba(245,109,42,0.2)]"
                    : "border border-[#f0dfd2] bg-white text-[#53606f] hover:bg-[#fffaf7]"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          <div className="mt-6 overflow-hidden rounded-[20px] border border-[#f1dfd2] bg-white">
            <div className="grid min-w-[700px] grid-cols-[1.6fr_0.9fr_0.8fr_0.8fr_0.6fr] gap-4 border-b border-[#f3e5dc] bg-[#fff6f2] px-4 py-3 text-sm font-medium text-[#6b564b]">
              <span>Title</span>
              <span>Type</span>
              <span>Status</span>
              <span>Updated</span>
              <span>Actions</span>
            </div>

            {jobs.map((job) => (
              <div
                key={job.title}
                className="grid min-w-[700px] grid-cols-[1.6fr_0.9fr_0.8fr_0.8fr_0.6fr] items-center gap-4 border-b border-[#edf1f4] px-4 py-4 text-sm last:border-b-0"
              >
                <div className="font-medium text-[#2d3340]">{job.title}</div>
                <div className="text-[#4d5561]">{job.type}</div>
                <div>
                  <StatusBadge status={job.status} />
                </div>
                <div className="text-[#5f6875]">{job.updated}</div>
                <button type="button" className="text-[#d85c2a] hover:text-[#bf4d1e]">
                  View
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
