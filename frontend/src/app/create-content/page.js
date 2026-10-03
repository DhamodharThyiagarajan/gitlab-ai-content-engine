"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import {
  FiArrowRight,
  FiBookOpen,
  FiCheckCircle,
  FiClock,
  FiFileText,
  FiImage,
  FiLink2,
  FiLoader,
  FiMessageSquare,
  FiShield,
  FiUploadCloud,
  FiZap,
} from "react-icons/fi";
import AppLayout from "@/components/layout/AppLayout";

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

const tabStyles = {
  active: "border-b-2 border-[#f97316] bg-[#111827] text-slate-100",
  inactive: "text-slate-400 hover:text-slate-200",
};

const workflowSteps = [
  "Upload document",
  "Extract source context",
  "Build context pack",
  "Run AI workflow",
  "Review & publish",
];
const completedStepsByStatus = {
  intake: 1,
  context_preparation: 3,
  review: 4,
  approved: 5,
  published: 5,
};

export default function CreateContentPage() {
  const { user } = useAuth();
  const [selectedTab, setSelectedTab] = useState("Templates");
  const [selectedFile, setSelectedFile] = useState(null);
  const [rawText, setRawText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [statusLog, setStatusLog] = useState([
    "Waiting for document upload",
    "Ready to process source input",
  ]);

  const [form, setForm] = useState({
    title: "",
    content_type: "documentation",
    audience: "Developers",
    product_area: "General",
    channel: "Documentation",
  });

  const hasSelectedFile = Boolean(selectedFile);

  const progressPercent = useMemo(() => {
    if (!job) return 10;
    const statusMap = {
      intake: 20,
      context_preparation: 45,
      review: 80,
      failed: 100,
      published: 100,
    };
    return statusMap[job.status] ?? 60;
  }, [job]);

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileSelection = (event) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    if (file) {
      updateStatus(["Document uploaded successfully", "Ready to process source input"]);
    }
  };

  const updateStatus = (messages) => setStatusLog(messages);

  const handleSubmit = async () => {
    if (!user) {
      setError("Please sign in before processing a document.");
      return;
    }

    if (!selectedFile && !rawText.trim()) {
      setError("Please upload a document or paste raw text to process.");
      return;
    }

    if (!form.title.trim()) {
      setError("Please enter a title for your content job.");
      return;
    }

    setError("");
    setIsSubmitting(true);
    setJob(null);
    updateStatus([
      selectedFile ? "Uploading document..." : "Submitting raw text...",
      "Validating source content and metadata...",
    ]);

    try {
      const token = await user.getIdToken();
      let jobPayload;

      if (selectedFile) {
        const uploadForm = new FormData();
        uploadForm.append("title", form.title);
        uploadForm.append("content_type", form.content_type);
        uploadForm.append("audience", form.audience);
        uploadForm.append("product_area", form.product_area);
        uploadForm.append("channel", form.channel);
        uploadForm.append("file", selectedFile);

        const uploadResponse = await fetch(`${BACKEND_URL}/api/content-jobs/upload`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: uploadForm,
        });

        const uploadData = await uploadResponse.json().catch(() => ({}));

        if (!uploadResponse.ok) {
          throw new Error(uploadData.detail || "Document upload failed.");
        }

        jobPayload = uploadData;
        updateStatus([
          "Document uploaded successfully",
          "Extracting source text and metadata...",
          "Preparing context package...",
        ]);
      } else {
        const createResponse = await fetch(`${BACKEND_URL}/api/content-jobs`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: form.title,
            content_type: form.content_type,
            audience: form.audience,
            product_area: form.product_area,
            channel: form.channel,
            source_text: rawText.trim(),
          }),
        });

        const createData = await createResponse.json().catch(() => ({}));

        if (!createResponse.ok) {
          throw new Error(createData.detail || "Raw text submission failed.");
        }

        jobPayload = createData;
        updateStatus([
          "Raw text submitted successfully",
          "Extracting source context...",
          "Preparing context package...",
        ]);
      }

      const runResponse = await fetch(`${BACKEND_URL}/api/content-jobs/${jobPayload.id}/run`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      const runData = await runResponse.json().catch(() => ({}));

      if (!runResponse.ok) {
        throw new Error(runData.detail || "Content workflow failed.");
      }

      setJob(runData);

      updateStatus([
        selectedFile ? "Document uploaded successfully" : "Raw text submitted successfully",
        "Source context extracted",
        "AI workflow completed",
        "Draft generated. Navigate to the Review panel to review it.",
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong while processing the source.");
      updateStatus([selectedFile ? "Upload failed" : "Processing failed", "Please review the input and try again."]);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout initialSelectedNav="Create Content">
      <div className="max-h-[calc(100vh-12rem)] overflow-y-auto px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-6">
        <div className="w-full min-w-0 rounded-[22px] border border-[#2d3748] bg-[#111827] p-4 shadow-[0_2px_12px_rgba(2,6,23,0.35)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm font-medium text-slate-300">GitLab AI</div>
          </div>

          <div className="mt-5">
            <h1 className="text-2xl font-semibold tracking-[-0.05em] text-slate-100 sm:text-[2.2rem]">
              Create Content
            </h1>
          </div>

          <p className="mt-2 max-w-[640px] text-sm text-slate-400 sm:text-[1rem]">
            Upload a source document, extract the technical context, and run the AI workflow to produce a ready-to-review draft.
          </p>

          <div className="mt-5 flex gap-3 border-b border-[#2d3748] pb-2">
            {["Templates", "Custom", "From Existing"].map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setSelectedTab(tab)}
                className={`rounded-t-lg px-3 py-2 text-sm font-medium transition ${
                  selectedTab === tab ? tabStyles.active : tabStyles.inactive
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="mt-6 grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
            <div className="rounded-[18px] border border-[#2d3748] bg-[#0f172a] p-4 shadow-[inset_0_0_0_1px_rgba(148,163,184,0.08)]">
              <div className="flex items-center justify-between gap-2">
                <div className="text-sm font-medium text-slate-300">Document intake</div>
                <div className="text-xs text-slate-400">{selectedFile ? selectedFile.name : "No file selected"}</div>
              </div>

              <label
                className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed px-6 py-10 text-center transition ${
                  hasSelectedFile
                    ? "border-emerald-500/80 bg-emerald-500/10 hover:border-emerald-400 hover:bg-emerald-500/15"
                    : "border-[#475569] bg-[#111827] hover:border-[#f97316] hover:bg-[#141d2d]"
                }`}
              >
                <div
                  className={`flex h-14 w-14 items-center justify-center rounded-full ${
                    hasSelectedFile ? "bg-emerald-500/20 text-emerald-300" : "bg-[#1e293b] text-[#f8fafc]"
                  }`}
                >
                  {hasSelectedFile ? <FiCheckCircle className="h-6 w-6" /> : <FiUploadCloud className="h-6 w-6" />}
                </div>
                <div className={`mt-4 text-base font-medium ${hasSelectedFile ? "text-emerald-200" : "text-slate-200"}`}>
                  {hasSelectedFile ? "Document uploaded" : "Upload source document"}
                </div>
                <div className={`mt-1 text-sm ${hasSelectedFile ? "text-emerald-300" : "text-slate-400"}`}>
                  {hasSelectedFile ? selectedFile.name : "PDF, DOCX, TXT, MD, or CSV"}
                </div>
                <input type="file" className="hidden" onChange={handleFileSelection} />
              </label>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <label className="block text-sm text-slate-300 sm:col-span-2">
                  <span className="mb-1 block">Raw text source</span>
                  <textarea
                    value={rawText}
                    onChange={(event) => setRawText(event.target.value)}
                    rows={5}
                    className="w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-slate-100 outline-none placeholder:text-slate-500 focus:border-[#f97316]"
                    placeholder="Paste release notes, product context, or any raw text here. This can be processed even without uploading a file."
                  />
                </label>

                <label className="block text-sm text-slate-300">
                  <span className="mb-1 block">Title</span>
                  <input
                    value={form.title}
                    onChange={(event) => updateField("title", event.target.value)}
                    className="w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-slate-100 outline-none placeholder:text-slate-500 focus:border-[#f97316]"
                    placeholder="Product onboarding guide"
                  />
                </label>

                <label className="block text-sm text-slate-300">
                  <span className="mb-1 block">Content type</span>
                  <select
                    value={form.content_type}
                    onChange={(event) => updateField("content_type", event.target.value)}
                    className="w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-slate-100 outline-none focus:border-[#f97316]"
                  >
                    <option value="documentation">Documentation</option>
                    <option value="release_notes">Release Notes</option>
                    <option value="api_docs">API Documentation</option>
                    <option value="blog_post">Blog Post</option>
                    <option value="onboarding_guide">Onboarding Guide</option>
                    <option value="custom">Custom</option>
                  </select>
                </label>

                <label className="block text-sm text-slate-300">
                  <span className="mb-1 block">Audience</span>
                  <input
                    value={form.audience}
                    onChange={(event) => updateField("audience", event.target.value)}
                    className="w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-slate-100 outline-none focus:border-[#f97316]"
                    placeholder="Developers"
                  />
                </label>

                <label className="block text-sm text-slate-300">
                  <span className="mb-1 block">Product area</span>
                  <input
                    value={form.product_area}
                    onChange={(event) => updateField("product_area", event.target.value)}
                    className="w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-slate-100 outline-none focus:border-[#f97316]"
                    placeholder="General"
                  />
                </label>

                <label className="block text-sm text-slate-300 sm:col-span-2">
                  <span className="mb-1 block">Channel</span>
                  <select
                    value={form.channel}
                    onChange={(event) => updateField("channel", event.target.value)}
                    className="w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-slate-100 outline-none focus:border-[#f97316]"
                  >
                    <option value="Documentation">Documentation</option>
                    <option value="Blog">Blog</option>
                    <option value="Release Notes">Release Notes</option>
                    <option value="Knowledge Base">Knowledge Base</option>
                  </select>
                </label>
              </div>

              <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2 text-slate-300">
                  <button type="button" className="rounded-lg border border-[#374151] bg-[#111827] p-2">
                    <FiFileText className="h-4 w-4" />
                  </button>
                  <button type="button" className="rounded-lg border border-[#374151] bg-[#111827] p-2">
                    <FiLink2 className="h-4 w-4" />
                  </button>
                </div>

                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#f97316] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_10px_18px_rgba(249,115,22,0.22)] transition hover:bg-[#ea580c] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSubmitting ? (
                    <>
                      <FiLoader className="h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <FiZap className="h-4 w-4" />
                      {selectedFile ? "Process Document" : rawText.trim() ? "Process Raw Text" : "Process Source"}
                    </>
                  )}
                </button>
              </div>

              {error ? <div className="mt-4 rounded-xl border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</div> : null}
            </div>

            <div className="rounded-[18px] border border-[#2d3748] bg-[#0f172a] p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium text-slate-300">Workflow status</div>
                <div className="text-xs text-slate-400">{job?.status || "idle"}</div>
              </div>

              <div className="mt-4">
                <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
                  <span>Progress</span>
                  <span>{progressPercent}%</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-[#1e293b]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[#f59e0b] via-[#f97316] to-[#fb7185] transition-all duration-500"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {workflowSteps.map((step, index) => {
                  const isDone = index < (completedStepsByStatus[job?.status] ?? 0);

                  return (
                    <div key={step} className="flex items-center gap-3 rounded-xl border border-[#2d3748] bg-[#111827] px-3 py-2">
                      <div
                        className={`flex h-7 w-7 items-center justify-center rounded-full ${
                          isDone ? "bg-emerald-500/20 text-emerald-300" : "bg-[#1e293b] text-slate-400"
                        }`}
                      >
                        {isDone ? <FiCheckCircle className="h-4 w-4" /> : <FiClock className="h-4 w-4" />}
                      </div>
                      <span className="text-sm text-slate-200">{step}</span>
                    </div>
                  );
                })}
              </div>

              <div className="mt-5 rounded-xl border border-[#2d3748] bg-[#111827] p-3">
                <div className="text-xs uppercase tracking-[0.12em] text-slate-400">Operations log</div>
                <ul className="mt-3 space-y-2 text-sm text-slate-300">
                  {statusLog.map((log) => (
                    <li key={log} className="flex items-start gap-2">
                      <FiArrowRight className="mt-0.5 h-3.5 w-3.5 text-[#f97316]" />
                      <span>{log}</span>
                    </li>
                  ))}
                </ul>
                {job?.status === "review" && (
                  <div className="mt-4 flex flex-col gap-2 border-t border-[#2d3748] pt-4 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-sm text-slate-300">Draft generated. Open the Review panel to review it.</p>
                    <Link href="/review" className="inline-flex items-center justify-center rounded-lg bg-[#f97316] px-3 py-2 text-sm font-semibold text-white transition hover:bg-[#ea580c]">
                      Go to Review panel
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
