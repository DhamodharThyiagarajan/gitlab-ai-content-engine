import json
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.entities import Draft, ContentJob, AuditEvent
from app.auth.security import require_roles
from app.services import gitlab_publisher

router = APIRouter(prefix="/publish", tags=["publishing"])


class ExportIn(BaseModel):
    draft_id: int
    format: str = "markdown"          # markdown | cms_json
    create_merge_request: bool = False  # optional GitLab MR (needs GITLAB_TOKEN + GITLAB_PROJECT_ID)


def _front_matter(job, draft, approver) -> str:
    return (
        "---\n"
        f"title: \"{job.title}\"\n"
        f"content_type: {job.content_type}\n"
        f"audience: {job.audience}\n"
        f"channel: {job.channel}\n"
        f"owner: {job.owner.name if job.owner else 'unknown'}\n"
        f"status: approved\n"
        f"approved_by: {approver.name}\n"
        f"draft_version: {draft.version}\n"
        f"quality_score: {job.quality_score}\n"
        f"exported_at: {datetime.now(timezone.utc).isoformat()}\n"
        "---\n\n"
    )


@router.post("/export")
def export(body: ExportIn, db: Session = Depends(get_db), user=Depends(require_roles("approver", "admin"))):
    if body.format not in {"markdown", "cms_json"}:
        raise HTTPException(400, "format must be 'markdown' or 'cms_json'")
    draft = db.get(Draft, body.draft_id)
    if not draft:
        raise HTTPException(404, "Draft not found")
    if not draft.approved:
        raise HTTPException(409, "Draft must be approved before export")
    job = db.get(ContentJob, draft.job_id)
    if not job:
        raise HTTPException(404, "Content job not found")
    root = Path("exports"); root.mkdir(exist_ok=True)
    safe = "".join(c.lower() if c.isalnum() else "-" for c in job.title).strip("-")[:80] or "content"
    markdown = _front_matter(job, draft, user) + draft.content
    if body.format == "cms_json":
        payload = {"title": job.title, "slug": safe, "content_type": job.content_type, "audience": job.audience,
                   "channel": job.channel, "owner": job.owner.name if job.owner else None, "status": "approved",
                   "approved_by": user.name, "draft_version": draft.version, "body_markdown": draft.content,
                   "source_refs": json.loads(draft.source_refs or "[]")}
        filename, text = f"{job.id}-{safe}.json", json.dumps(payload, indent=2)
    else:
        filename, text = f"{job.id}-{safe}.md", markdown
    (root / filename).write_text(text, encoding="utf-8")

    merge_request, warning = None, None
    if body.create_merge_request:
        if not gitlab_publisher.is_configured():
            warning = "GitLab merge request skipped: GITLAB_TOKEN / GITLAB_PROJECT_ID are not configured."
        else:
            try:
                merge_request = gitlab_publisher.create_merge_request(job.id, f"{job.id}-{safe}.md", markdown, job.title)
            except Exception as exc:  # export itself already succeeded
                warning = f"GitLab merge request failed: {str(exc)[:200]}"

    job.status = "published"
    db.add(AuditEvent(job_id=job.id, actor_id=user.id, event_type="document_published",
                      details=json.dumps({"file": filename, "format": body.format, "draft_version": draft.version,
                                          "merge_request": merge_request, "warning": warning})))
    db.commit()
    return {"filename": filename, "path": str(root / filename), "content": text, "format": body.format,
            "status": job.status, "merge_request": merge_request, "warning": warning}
