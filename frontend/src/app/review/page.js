"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import { useAuth } from "@/hooks/useAuth";

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

function ReviewList({ title, items, empty }) {
  const values = (Array.isArray(items) ? items : items ? [items] : []).map((item) => {
    if (typeof item === "string") return item.trim();
    if (!item || typeof item !== "object") return "";
    const refs = Array.isArray(item.source_refs) ? item.source_refs : item.source_refs ? [item.source_refs] : [];
    return [item.fact || item.claim || item.text || item.description || "", ...refs.filter(Boolean).map((source) => `Source: ${source}`)].filter(Boolean).join(" | ").trim();
  }).filter(Boolean);
  return <section>
    {title && <h3 className="text-sm font-semibold text-slate-200">{title}</h3>}
    {values.length ? <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-400">{values.map((item, index) => <li key={`${index}-${item}`} className="flex gap-2"><span className="text-orange-300">-</span><span>{item}</span></li>)}</ul> : <p className="mt-2 text-sm text-slate-500">{empty}</p>}
  </section>;
}

export default function ReviewPage() {
  const { user, userProfile } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [comments, setComments] = useState("");
  const [action, setAction] = useState("");
  const [stage, setStage] = useState("full");
  const [exportFormat, setExportFormat] = useState("markdown");
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState("");
  const [diffText, setDiffText] = useState("");
  const role = (userProfile?.role || "writer").toLowerCase();
  const canApprove = ["approver", "admin"].includes(role);
  const canPublish = ["approver", "admin"].includes(role);

  useEffect(() => {
    if (!user) return;
    let active = true;
    (async () => {
      try {
        const token = await user.getIdToken();
        const response = await fetch(`${BACKEND_URL}/api/content-jobs`, { headers: { Authorization: `Bearer ${token}` } });
        const data = await response.json().catch(() => []);
        if (!response.ok) throw new Error(data.detail || "Unable to load review jobs.");
        const reviewJobs = data.filter((job) => ["review", "revision_requested", "approved", "publish_ready", "published"].includes(job.status));
        if (active) { setJobs(reviewJobs); setSelectedId(reviewJobs[0] ? String(reviewJobs[0].id) : ""); }
      } catch (err) { if (active) setError(err.message || "Unable to load review jobs."); }
      finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, [user]);

  useEffect(() => {
    if (!user || !selectedId) { setDetail(null); return; }
    let active = true;
    setDetail(null);
    (async () => {
      try {
        const token = await user.getIdToken();
        const response = await fetch(`${BACKEND_URL}/api/content-jobs/${selectedId}`, { headers: { Authorization: `Bearer ${token}` } });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || "Unable to load this document.");
        if (active) setDetail(data);
      } catch (err) { if (active) setError(err.message || "Unable to load this document."); }
    })();
    return () => { active = false; };
  }, [user, selectedId]);

  const draft = detail?.drafts?.at(-1);
  const review = draft?.technical_review || detail?.technical_review || {};
  const formatDate = (value) => value ? new Date(value).toLocaleString() : "Not available";

  const refreshSelectedJob = async (token) => {
    const [jobResponse, listResponse] = await Promise.all([
      fetch(`${BACKEND_URL}/api/content-jobs/${selectedId}`, { headers: { Authorization: `Bearer ${token}` } }),
      fetch(`${BACKEND_URL}/api/content-jobs`, { headers: { Authorization: `Bearer ${token}` } }),
    ]);
    const jobData = await jobResponse.json().catch(() => ({}));
    const listData = await listResponse.json().catch(() => []);
    if (!jobResponse.ok) throw new Error(jobData.detail || "Unable to refresh this document.");
    if (!listResponse.ok) throw new Error(listData.detail || "Unable to refresh the review queue.");
    setDetail(jobData);
    setJobs(listData.filter((job) => ["review", "revision_requested", "approved", "publish_ready", "published"].includes(job.status)));
  };

  const submitReviewDecision = async (decision) => {
    if (!user || !draft) return;
    setAction(decision);
    setError("");
    setNotice("");
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${BACKEND_URL}/api/drafts/${draft.id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ decision, comments }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Unable to submit the review decision.");

      if (decision === "request_revision") {
        const refineResponse = await fetch(`${BACKEND_URL}/api/drafts/${draft.id}/refine`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ comments, stage }),
        });
        const refineData = await refineResponse.json().catch(() => ({}));
        if (!refineResponse.ok) throw new Error(refineData.detail || "Revision was requested, but refinement failed.");
        setNotice("Revision generated and returned to the review queue.");
        setComments("");
      } else {
        setNotice("Draft approved. It is ready to publish.");
      }
      await refreshSelectedJob(token);
    } catch (err) {
      setError(err.message || "Unable to complete this review action.");
      try { await refreshSelectedJob(await user.getIdToken()); } catch { /* keep the original action error */ }
    } finally {
      setAction("");
    }
  };

  const saveEdit = async () => {
    if (!user || !draft || !editText.trim()) return;
    setAction("edit"); setError(""); setNotice("");
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${BACKEND_URL}/api/drafts/${draft.id}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ content: editText, comments }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Unable to save the edit.");
      setEditing(false); setDiffText("");
      setNotice(`Edit saved as version ${data.version}. It must be approved again before publishing.`);
      await refreshSelectedJob(token);
    } catch (err) { setError(err.message || "Unable to save the edit."); } finally { setAction(""); }
  };

  const compareWith = async (otherId) => {
    if (!user || !draft || !otherId) { setDiffText(""); return; }
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${BACKEND_URL}/api/drafts/${otherId}/diff/${draft.id}`, { headers: { Authorization: `Bearer ${token}` } });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Unable to compare versions.");
      setDiffText(data.diff || "No differences between these versions.");
    } catch (err) { setError(err.message || "Unable to compare versions."); }
  };

  const publishDraft = async () => {
    if (!user || !draft) return;
    setAction("publish");
    setError("");
    setNotice("");
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${BACKEND_URL}/api/publish/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ draft_id: draft.id, format: exportFormat }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Unable to publish this document.");
      const file = new Blob([data.content], { type: exportFormat === "cms_json" ? "application/json" : "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(file);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = data.filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice(`Published successfully. ${data.filename} was downloaded.`);
      await refreshSelectedJob(token);
    } catch (err) {
      setError(err.message || "Unable to publish this document.");
    } finally {
      setAction("");
    }
  };

  return <AppLayout initialSelectedNav="Review">
    <div className="px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-8 xl:pb-10">
      <div className="rounded-[24px] border border-[#2d3748] bg-[#111827] p-4 shadow-[0_2px_8px_rgba(2,6,23,0.35)] sm:p-5 lg:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div><p className="text-xs font-medium uppercase tracking-[0.16em] text-orange-300">Documentation review</p><h1 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-100 sm:text-[2.1rem]">Review generated document</h1><p className="mt-2 text-sm text-slate-400">Read the customer facing Markdown alongside its technical evidence.</p></div>
          <label className="w-full sm:max-w-sm"><span className="mb-1.5 block text-xs font-medium text-slate-400">Review queue</span><select value={selectedId} onChange={(event) => setSelectedId(event.target.value)} className="w-full rounded-xl border border-[#374151] bg-[#0f172a] px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-orange-400"><option value="">Select a document</option>{jobs.map((job) => <option key={job.id} value={job.id}>{job.title} · #{job.id}</option>)}</select></label>
        </div>
        {error && <div role="alert" className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>}
        {notice && <div role="status" className="mt-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{notice}</div>}
        {loading ? <p className="py-16 text-center text-sm text-slate-400">Loading review queue…</p> : !jobs.length ? <div className="mt-6 rounded-2xl border border-dashed border-[#374151] px-6 py-14 text-center"><h2 className="font-medium text-slate-200">No documents are waiting for review</h2><p className="mt-2 text-sm text-slate-500">Generated drafts will appear here once their workflow completes.</p></div> : detail && draft ? <div className="mt-6 grid items-start gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(300px,0.75fr)]">
          <section className="min-w-0 overflow-hidden rounded-2xl border border-[#2d3748] bg-[#0f172a]">
            <header className="border-b border-[#2d3748] px-5 py-5 sm:px-7"><div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="text-xl font-semibold text-slate-100">{detail.title}</h2><p className="mt-1 text-sm text-slate-400">{detail.content_type} · {detail.audience}</p></div><span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-medium text-amber-200">{detail.status.replaceAll("_", " ")}</span></div><div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500"><span>Generated {formatDate(draft.generated_at || draft.created_at)}</span><span>Version {draft.version}</span><span>Channel: {detail.channel}</span></div></header>
            <div className="px-5 py-6 sm:px-7 sm:py-8"><MarkdownRenderer content={draft.final_document || draft.content || ""} /></div>
          </section>
          <aside className="space-y-4">
            <section className="rounded-2xl border border-[#2d3748] bg-[#0f172a] p-5"><div className="flex items-center justify-between gap-3"><h2 className="font-semibold text-slate-100">Technical review</h2><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${review.verdict === "PASS" ? "bg-emerald-400/10 text-emerald-300" : "bg-amber-400/10 text-amber-200"}`}>{review.verdict || "NEEDS REVIEW"}</span></div><div className="mt-4 grid grid-cols-2 gap-3"><div className="rounded-xl border border-[#2d3748] bg-[#111827] p-3"><p className="text-xs text-slate-500">Quality score</p><p className="mt-1 text-2xl font-semibold text-slate-100">{review.quality_score ?? detail.quality_score ?? "—"}<span className="ml-1 text-sm font-normal text-slate-500">/100</span></p></div><div className="rounded-xl border border-[#2d3748] bg-[#111827] p-3"><p className="text-xs text-slate-500">Supported facts</p><p className="mt-1 text-2xl font-semibold text-slate-100">{review.evidence_count ?? "—"}</p></div></div></section>
            <section className="space-y-5 rounded-2xl border border-[#2d3748] bg-[#0f172a] p-5"><ReviewList title="Supported information" items={review.supported_information || review.supported_sections || []} empty="No supported information was extracted." /><ReviewList title="Context gaps" items={review.context_gaps || review.missing_information || []} empty="No context gaps identified." /><ReviewList title="Unsupported claims" items={review.unsupported_claims || []} empty="No unsupported claims identified." /><ReviewList title="Technical risks" items={review.risks || draft.risk_flags || []} empty="No technical risks identified." /></section>
            <section className="rounded-2xl border border-[#2d3748] bg-[#0f172a] p-5"><h3 className="text-sm font-semibold text-slate-200">Source references</h3><ReviewList title="" items={review.source_refs || draft.source_refs || []} empty="No source references recorded." /></section>
            <section className="rounded-2xl border border-[#2d3748] bg-[#0f172a] p-5">
              <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-semibold text-slate-200">Versions ({detail.drafts?.length || 1})</h3>
                {['review', 'revision_requested'].includes(detail.status) && !editing && <button type="button" onClick={() => { setEditText(draft.content || ""); setEditing(true); }} className="text-xs font-semibold text-orange-300 hover:text-orange-200">Edit manually</button>}</div>
              {(detail.drafts?.length || 0) > 1 && <label className="mt-3 block text-xs text-slate-400">Compare an earlier version with v{draft.version}
                <select defaultValue="" onChange={(event) => compareWith(event.target.value)} className="mt-1.5 w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2 text-sm text-slate-100"><option value="">Select a version</option>{detail.drafts.filter((item) => item.id !== draft.id).map((item) => <option key={item.id} value={item.id}>Version {item.version} ({item.stage.replaceAll("_", " ")})</option>)}</select></label>}
              {diffText && <pre className="mt-3 max-h-64 overflow-auto rounded-xl border border-[#2d3748] bg-[#111827] p-3 text-xs leading-5 text-slate-300">{diffText.split("\n").map((line, index) => <div key={index} className={line.startsWith("+") && !line.startsWith("+++") ? "text-emerald-300" : line.startsWith("-") && !line.startsWith("---") ? "text-red-300" : ""}>{line || " "}</div>)}</pre>}
              {editing && <div className="mt-3"><textarea value={editText} onChange={(event) => setEditText(event.target.value)} rows={12} className="w-full resize-y rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 font-mono text-xs text-slate-100 outline-none focus:border-orange-400" />
                <div className="mt-3 grid gap-3 sm:grid-cols-2"><button type="button" onClick={() => setEditing(false)} className="rounded-xl border border-[#374151] bg-[#111827] px-4 py-2 text-sm font-semibold text-slate-200">Cancel</button><button type="button" disabled={Boolean(action)} onClick={saveEdit} className="rounded-xl bg-[#f97316] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{action === "edit" ? "Saving…" : "Save as new version"}</button></div></div>}
            </section>
            {['review', 'revision_requested'].includes(detail.status) && <section className="rounded-2xl border border-[#2d3748] bg-[#0f172a] p-5">
              <label className="block text-sm font-medium text-slate-200" htmlFor="review-comments">Reviewer comments</label>
              <textarea id="review-comments" value={comments} onChange={(event) => setComments(event.target.value)} rows={3} placeholder="Add guidance for the requested revision (optional)." className="mt-2 w-full resize-y rounded-xl border border-[#374151] bg-[#111827] px-3 py-2.5 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-orange-400" />
              <label className="mt-3 block text-xs text-slate-400">Revision scope
                <select value={stage} onChange={(event) => setStage(event.target.value)} className="mt-1.5 w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2 text-sm text-slate-100"><option value="full">Full revision (address comments)</option><option value="tone">Tone only</option><option value="structure">Structure only</option><option value="clarity">Clarity only</option><option value="technical">Technical accuracy only</option></select></label>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <button type="button" disabled={Boolean(action)} onClick={() => submitReviewDecision("request_revision")} className="rounded-xl border border-[#374151] bg-[#111827] px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:bg-[#182335] disabled:cursor-wait disabled:opacity-60">{action === "request_revision" ? "Generating revision…" : "Request Revision"}</button>
                {canApprove && <button type="button" disabled={Boolean(action)} onClick={() => submitReviewDecision("approve")} className="rounded-xl bg-[#f97316] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#ea580c] disabled:cursor-wait disabled:opacity-60">{action === "approve" ? "Approving…" : "Approve"}</button>}
              </div>
              {!canApprove && <p className="mt-3 text-xs text-slate-500">Only an approver or admin can approve this draft. Use Request Revision to send it back.</p>}
            </section>}
            {["approved", "publish_ready"].includes(detail.status) && canPublish && <section className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"><h3 className="font-semibold text-slate-100">Ready to publish</h3><p className="mt-1 text-sm text-slate-400">Publish the approved Markdown document and download a copy.</p><label className="mt-3 block text-xs text-slate-400">Export format<select value={exportFormat} onChange={(event) => setExportFormat(event.target.value)} className="mt-1.5 w-full rounded-xl border border-[#374151] bg-[#111827] px-3 py-2 text-sm text-slate-100"><option value="markdown">Markdown with front matter (.md)</option><option value="cms_json">CMS-ready JSON (.json)</option></select></label><button type="button" disabled={Boolean(action)} onClick={publishDraft} className="mt-4 w-full rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:cursor-wait disabled:opacity-60">{action === "publish" ? "Publishing…" : "Publish"}</button></section>}
            {["approved", "publish_ready"].includes(detail.status) && !canPublish && <p className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-200">Approved and waiting for an approver or admin to publish.</p>}
            {detail.status === "published" && <p className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 text-sm font-medium text-emerald-200">Published</p>}
          </aside>
        </div> : jobs.length ? <p className="py-16 text-center text-sm text-slate-400">Loading document…</p> : null}
      </div>
    </div>
  </AppLayout>;
}
