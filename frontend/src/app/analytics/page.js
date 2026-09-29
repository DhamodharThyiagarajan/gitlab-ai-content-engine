"use client";

import AppLayout from "@/components/layout/AppLayout";

const stats = [
  { label: "Total Content", value: 248, change: "+12%" },
  { label: "Published", value: 201, change: "+8%" },
  { label: "Drafts", value: 12, change: "-3%" },
  { label: "Avg. Time", value: "4.2h", change: "-1.4h" },
];

const bars = [42, 58, 30, 68, 55, 72, 61];

export default function AnalyticsPage() {
  return (
    <AppLayout initialSelectedNav="Analytics">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#f0dfd2] bg-[#fffaf7] p-4 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[2.1rem]">Analytics</h1>
              <p className="mt-2 text-sm text-[#6a6f76] sm:text-[1rem]">
                Track performance, publishing velocity, and content quality across workflows.
              </p>
            </div>

            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl border border-[#f1d7c3] bg-[#fff5ef] px-4 py-2.5 text-sm font-medium text-[#2e3641] transition hover:bg-[#fef1e8]"
            >
              Last 30 days
            </button>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-[20px] border border-[#f1dfd2] bg-white p-4">
                <div className="text-sm text-[#67707a]">{stat.label}</div>
                <div className="mt-3 flex items-end justify-between">
                  <div className="text-[2rem] font-semibold tracking-[-0.05em] text-[#1f2328]">{stat.value}</div>
                  <div className="text-sm font-medium text-[#2a9d67]">{stat.change}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-[20px] border border-[#f1dfd2] bg-white p-4">
            <div className="mb-4 text-lg font-semibold text-[#1f2328]">Content Trend</div>
            <div className="flex h-44 items-end gap-3">
              {bars.map((bar, index) => (
                <div key={index} className="flex flex-1 flex-col items-center gap-2">
                  <div
                    className="w-full rounded-t-xl bg-gradient-to-t from-[#f56d2a] to-[#f9b38f]"
                    style={{ height: `${bar}%` }}
                  />
                  <span className="text-xs text-[#6b717b]">{["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"][index]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
