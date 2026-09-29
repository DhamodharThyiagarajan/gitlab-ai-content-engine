"use client";

import AppLayout from "@/components/layout/AppLayout";

const reviews = [
  { title: "Release Notes v16.4", type: "Release Notes", author: "Dhamo", submitted: "4 hours ago", priority: "High" },
  { title: "API Reference Draft", type: "API Docs", author: "Dhamo", submitted: "6 hours ago", priority: "Medium" },
  { title: "User Onboarding Guide", type: "Guide", author: "Dhamo", submitted: "1 day ago", priority: "Low" },
  { title: "Architecture Overview", type: "Documentation", author: "Dhamo", submitted: "2 days ago", priority: "Medium" },
];

function PriorityBadge({ priority }) {
  const palette = {
    High: "bg-[#fff0e6] text-[#d97932]",
    Medium: "bg-[#eef3ff] text-[#4b6ed9]",
    Low: "bg-[#eafaf0] text-[#2c9d68]",
  };

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${palette[priority] || "bg-[#edf2f7] text-[#49505a]"}`}>
      {priority}
    </span>
  );
}

export default function ReviewPage() {
  return (
    <AppLayout initialSelectedNav="Review">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#f0dfd2] bg-[#fffaf7] p-4 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[2.1rem]">Review</h1>
              <p className="mt-2 text-sm text-[#6a6f76] sm:text-[1rem]">
                Review approved AI drafts and finalize content before publishing.
              </p>
            </div>

            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl bg-[#f56d2a] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_10px_18px_rgba(245,109,42,0.22)] transition hover:bg-[#e55f1c]"
            >
              Review Queue
            </button>
          </div>

          <div className="mt-6 grid gap-4 xl:grid-cols-2">
            {reviews.map((review) => (
              <div key={review.title} className="rounded-[20px] border border-[#f0dfd2] bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-[#1f2328]">{review.title}</h2>
                    <p className="mt-1 text-sm text-[#5c6470]">{review.type}</p>
                  </div>
                  <PriorityBadge priority={review.priority} />
                </div>

                <div className="mt-5 flex items-center justify-between text-sm text-[#5d6875]">
                  <span>Author: {review.author}</span>
                  <span>{review.submitted}</span>
                </div>

                <div className="mt-5 flex gap-3">
                  <button
                    type="button"
                    className="flex-1 rounded-xl bg-[#f56d2a] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#e55f1c]"
                  >
                    Review
                  </button>
                  <button
                    type="button"
                    className="flex-1 rounded-xl border border-[#f0dfd2] bg-[#fffaf7] px-4 py-2.5 text-sm font-semibold text-[#2e3641] transition hover:bg-[#fff3ed]"
                  >
                    Request Changes
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
