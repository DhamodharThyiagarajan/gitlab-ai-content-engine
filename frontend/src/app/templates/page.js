"use client";

import AppLayout from "@/components/layout/AppLayout";

const templates = [
  { name: "Release Notes", type: "Documentation", usage: "42", updated: "2 hours ago" },
  { name: "API Overview", type: "Reference", usage: "18", updated: "5 hours ago" },
  { name: "Customer Newsletter", type: "Marketing", usage: "11", updated: "1 day ago" },
  { name: "Migration Guide", type: "Guide", usage: "23", updated: "2 days ago" },
  { name: "Roadmap Summary", type: "Planning", usage: "9", updated: "3 days ago" },
];

export default function TemplatesPage() {
  return (
    <AppLayout initialSelectedNav="Templates">
      <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
        <div className="rounded-[24px] border border-[#f0dfd2] bg-[#fffaf7] p-4 shadow-[0_2px_8px_rgba(15,23,42,0.02)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-[-0.04em] text-[#1f2328] sm:text-[2.1rem]">Templates</h1>
              <p className="mt-2 text-sm text-[#6a6f76] sm:text-[1rem]">
                Reuse proven content structures to keep every draft consistent and fast.
              </p>
            </div>

            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl bg-[#f56d2a] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_10px_18px_rgba(245,109,42,0.22)] transition hover:bg-[#e55f1c]"
            >
              New Template
            </button>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {templates.map((template) => (
              <div key={template.name} className="rounded-[20px] border border-[#f0dfd2] bg-white p-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-[#1f2328]">{template.name}</h2>
                  <span className="rounded-full bg-[#fff0e6] px-2.5 py-1 text-xs font-medium text-[#d97932]">{template.type}</span>
                </div>

                <div className="mt-5 grid grid-cols-2 gap-3 text-sm text-[#5d6875]">
                  <div>
                    <div className="text-xs uppercase tracking-[0.08em] text-[#857f7a]">Usage</div>
                    <div className="mt-1 text-base font-semibold text-[#1f2328]">{template.usage}</div>
                  </div>
                  <div>
                    <div className="text-xs uppercase tracking-[0.08em] text-[#857f7a]">Updated</div>
                    <div className="mt-1 text-base font-semibold text-[#1f2328]">{template.updated}</div>
                  </div>
                </div>

                <button
                  type="button"
                  className="mt-5 w-full rounded-xl border border-[#f0dfd2] bg-[#fffaf7] px-3 py-2.5 text-sm font-medium text-[#2e3641] transition hover:bg-[#fff3ed]"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
