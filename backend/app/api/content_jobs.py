from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Form
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import ContentJob,Draft,AuditEvent,Review,User
from app.auth.security import get_current_user, require_roles
from app.services.document_extractor import extract_document
from ai.common import clean_review_items, clean_source_refs, fact_sources, normalize_review_payload
router=APIRouter(prefix="/content-jobs",tags=["content-jobs"])
jobs_router=APIRouter(prefix="/jobs",tags=["content-jobs"])
context_router=APIRouter(prefix="/context-pack",tags=["context"])
UPLOAD_DIR=Path("data")/"uploads"; UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
class JobIn(BaseModel):
    title:str=Field(min_length=3); content_type:str; audience:str; product_area:str="General"; channel:str="Documentation"; source_text:str=Field(min_length=10)
@router.post("")
def create(body:JobIn,db:Session=Depends(get_db),user=Depends(require_roles("writer","admin"))):
    job=ContentJob(**body.model_dump(),owner_id=user.id,status="intake"); db.add(job); db.commit(); db.refresh(job); db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="job_created",details="Content job created")); db.commit(); return serialize(job)
@router.post("/upload")
async def create_from_upload(title:str=Form(...),content_type:str=Form("documentation"),audience:str=Form("Developers"),product_area:str=Form("General"),channel:str=Form("Documentation"),file:UploadFile=File(...),db:Session=Depends(get_db),user=Depends(require_roles("writer","admin"))):
    filename=Path(file.filename or "document").name; data=await file.read()
    if not data: raise HTTPException(400,"Uploaded file is empty")
    if len(data)>20*1024*1024: raise HTTPException(413,"Maximum upload size is 20 MB")
    try: extracted=extract_document(filename,data)
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
    stored=UPLOAD_DIR/f"{uuid4().hex}_{filename}"; stored.write_bytes(data)
    source=f"DOCUMENT: {filename}\nCONTENT TYPE: {extracted.content_type}\nPAGES/UNITS: {extracted.pages}\nSTORED FILE: {stored.as_posix()}\n\n{extracted.text}"
    job=ContentJob(title=title.strip(),content_type=content_type,audience=audience,product_area=product_area,channel=channel,source_text=source,owner_id=user.id,status="intake"); db.add(job); db.commit(); db.refresh(job)
    db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="document_uploaded",details=json.dumps({"filename":filename,"pages":extracted.pages,"source_refs":extracted.source_refs}))); db.commit(); return serialize(job,True)
@router.get("")
def list_jobs(db:Session=Depends(get_db),user=Depends(get_current_user)):
    query=db.query(ContentJob)
    if user.role == "writer": query=query.filter(ContentJob.owner_id==user.id)
    return [serialize(x) for x in query.order_by(ContentJob.created_at.desc()).all()]
@router.get("/{job_id}")
def get_job(job_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    job=db.get(ContentJob,job_id)
    if not job: raise HTTPException(404,"Job not found")
    if user.role == "writer" and job.owner_id != user.id: raise HTTPException(403,"Writers can only access their own jobs")
    return serialize(job,True)

jobs_router.add_api_route("/{job_id}", get_job, methods=["GET"])
@router.post("/{job_id}/run")
async def run(job_id:int,db:Session=Depends(get_db),user=Depends(require_roles("writer","admin"))):
    job=db.get(ContentJob,job_id)
    if not job: raise HTTPException(404,"Job not found")
    if user.role == "writer" and job.owner_id != user.id: raise HTTPException(403,"Writers can only run their own jobs")
    job.status="context_preparation"; db.commit()
    try:
        # Keep the API importable when optional AI workflow dependencies are
        # not installed; only workflow execution needs CrewAI.
        from ai.workflow import ContentWorkflow
        result=await ContentWorkflow().run(job)
    except Exception as exc:
        from ai.workflow import InsufficientContext
        job.status="failed"; db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="workflow_failed",details=str(exc)[:4000])); db.commit()
        if isinstance(exc,InsufficientContext): raise HTTPException(422,f"Insufficient context: {exc}") from exc
        raise HTTPException(502,f"AI workflow failed: {exc}") from exc
    job.context_pack=result["context"]; job.quality_score=result["quality_score"]; job.status="review"
    version=max([d.version for d in job.drafts],default=0)+1
    draft=Draft(job_id=job.id,version=version,content=result["content"],stage="publishing_preparation",source_refs=json.dumps(json.loads(result["context"]).get("source_refs",[])),risk_flags=json.dumps(result["risks"]),reviewer_notes=result["technical_review"])
    db.add(draft); db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="workflow_completed",details=json.dumps({"agents":result.get("agent_trace",[]),"quality_score":result["quality_score"],"prompt_version":result.get("prompt_version"),"orchestrator":result.get("orchestrator")}))); db.commit(); db.refresh(job); return serialize(job,True)

class ContextPackIn(BaseModel):
    job_id:int
@context_router.post("")
async def build_context_pack(body:ContextPackIn,db:Session=Depends(get_db),user=Depends(require_roles("writer","admin"))):
    """Normalize inputs, retrieve related knowledge and return the structured context pack (no drafting)."""
    job=db.get(ContentJob,body.job_id)
    if not job: raise HTTPException(404,"Job not found")
    if user.role=="writer" and job.owner_id!=user.id: raise HTTPException(403,"Writers can only prepare their own jobs")
    from ai.workflow import ContentWorkflow, InsufficientContext
    try: pack=await ContentWorkflow().prepare_context(job)
    except InsufficientContext as exc: raise HTTPException(422,f"Insufficient context: {exc}") from exc
    job.context_pack=json.dumps(pack,indent=2); job.status="context_preparation"
    db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="context_prepared",details=json.dumps({"facts":len(pack["facts"]),"gaps":len(pack["gaps"])})))
    db.commit(); return {"job_id":job.id,"status":job.status,"context_pack":pack}
@router.get("/{job_id}/audit")
def audit_log(job_id:int,db:Session=Depends(get_db),user=Depends(require_roles("reviewer","approver","admin"))):
    job=db.get(ContentJob,job_id)
    if not job: raise HTTPException(404,"Job not found")
    names={u.id:u.name for u in db.query(User).all()}
    return [{"id":e.id,"event_type":e.event_type,"actor":names.get(e.actor_id,"system"),"details":e.details,"created_at":(e.created_at or datetime.now(timezone.utc)).isoformat()} for e in sorted(job.audit_events,key=lambda e:e.id)]

def serialize(job,detail=False):
    created_at = job.created_at or datetime.now(timezone.utc)
    out={"id":job.id,"title":job.title,"content_type":job.content_type,"audience":job.audience,"product_area":job.product_area,"channel":job.channel,"status":job.status,"quality_score":job.quality_score,"created_at":created_at.isoformat()}
    if detail:
        drafts = sorted(job.drafts, key=lambda draft: draft.version)
        serialized_drafts = []
        for draft in drafts:
            technical_review = normalize_review_payload(
                draft.reviewer_notes or "{}",
                fallback_source_refs=json.loads(draft.source_refs or "[]"),
            )
            generated_at = technical_review.get("generated_at") or (draft.created_at or created_at).isoformat()
            serialized_drafts.append({"id":draft.id,"version":draft.version,"content":draft.content,"final_document":draft.content,"stage":draft.stage,"source_refs":json.loads(draft.source_refs or "[]"),"risk_flags":json.loads(draft.risk_flags or "[]"),"reviewer_notes":draft.reviewer_notes,"technical_review":technical_review,"approved":draft.approved,"generated_at":generated_at})
        latest = serialized_drafts[-1] if serialized_drafts else None
        out.update({"source_text":job.source_text,"context_pack":job.context_pack,"quality_score":job.quality_score,"final_document":latest["final_document"] if latest else "","technical_review":latest["technical_review"] if latest else {},"drafts":serialized_drafts})
    return out


