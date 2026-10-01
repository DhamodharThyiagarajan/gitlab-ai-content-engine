from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.entities import Draft, ContentJob, AuditEvent
from app.auth.security import require_roles
router=APIRouter(prefix="/publish",tags=["publishing"])
class ExportIn(BaseModel): draft_id:int
@router.post("/export")
def export(body:ExportIn,db:Session=Depends(get_db),user=Depends(require_roles("approver","admin"))):
    draft=db.get(Draft,body.draft_id)
    if not draft: raise HTTPException(404,"Draft not found")
    if not draft.approved: raise HTTPException(409,"Draft must be approved before export")
    job=db.get(ContentJob,draft.job_id)
    if not job: raise HTTPException(404,"Content job not found")
    root=Path("exports"); root.mkdir(exist_ok=True)
    safe="".join(c.lower() if c.isalnum() else "-" for c in job.title).strip("-")[:80]
    path=root/f"{job.id}-{safe or 'content'}.md"; path.write_text(draft.content,encoding="utf-8")
    job.status="published"
    db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="document_published",details=f"Exported {path.name}"))
    db.commit()
    return {"filename":path.name,"path":str(path),"content":draft.content,"status":job.status}
