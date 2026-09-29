"use client";

import AppLayout from "@/components/layout/AppLayout";

const articles = [
  { title: "AI Content Workflow", category: "Process", status: "Published", updated: "2 hours ago" },
  { title: "Release Notes Standards", category: "Documentation", status: "Published", updated: "5 hours ago" },
  { title: "API Documentation Checklist", category: "Reference", status: "Draft", updated: "1 day ago" },
  { title: "Brand Voice Guidelines", category: "Marketing", status: "Published", updated: "2 days ago" },
  { title: "Onboarding Content Playbook", category: "Customer Success", status: "Draft", updated: "3 days ago" },
];

function StatusBadge({ status }) {
  const palette = {
    Published: "bg-[#eafaf0] text-[#2a9d67]",
    Draft: "bg-[#fff0e5] text-[#d38b31]",
  };

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${palette[status] || "bg-[#edf2f7] text-[#49505a]"}`}>
      {status}
    </span>
  );
}

export default function KnowledgeBasePage() {
  return (
    <AppLayout initialSelectedNav="Knowledge Base">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#f0dfd2] bg-[#fffaf7] p-4 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[2.1rem]">Knowledge Base</h1>
              <p className="mt-2 text-sm text-[#6a6f76] sm:text-[1rem]">
                Store reusable content guidance and reference material for your teams.
              </p>
            </div>

            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl border border-[#f1d7c3] bg-[#fff5ef] px-4 py-2.5 text-sm font-medium text-[#2e3641] transition hover:bg-[#fef1e8]"
            >
              New Article
            </button>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {articles.map((article) => (
              <div key={article.title} className="rounded-[20px] border border-[#f0dfd2] bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-[0.08em] text-[#8a7d75]">{article.category}</p>
                    <h2 className="mt-2 text-lg font-semibold text-[#1f2328]">{article.title}</h2>
                  </div>
                  <StatusBadge status={article.status} />
                </div>

                <div className="mt-5 flex items-center justify-between text-sm text-[#5d6875]">
                  <span>Updated</span>
                  <span>{article.updated}</span>
                </div>

                <button
                  type="button"
                  className="mt-5 w-full rounded-xl border border-[#f0dfd2] bg-[#fffaf7] px-3 py-2.5 text-sm font-medium text-[#2e3641] transition hover:bg-[#fff3ed]"
                >
                  Open Article
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
