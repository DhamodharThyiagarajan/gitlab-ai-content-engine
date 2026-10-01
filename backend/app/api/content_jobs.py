from __future__ import annotations
import json
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Form
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import ContentJob,Draft,AuditEvent
from app.auth.security import get_current_user, require_roles
from app.orchestration.workflow import ContentWorkflow
from app.services.document_extractor import extract_document
router=APIRouter(prefix="/content-jobs",tags=["content-jobs"])
jobs_router=APIRouter(prefix="/jobs",tags=["content-jobs"])
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
    try: result=await ContentWorkflow().run(job)
    except Exception as exc:
        job.status="failed"; db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="workflow_failed",details=str(exc)[:4000])); db.commit(); raise HTTPException(502,f"AI workflow failed: {exc}") from exc
    job.context_pack=result["context"]; job.quality_score=result["quality_score"]; job.status="review"
    version=max([d.version for d in job.drafts],default=0)+1
    draft=Draft(job_id=job.id,version=version,content=result["content"],stage="publishing_preparation",source_refs=json.dumps(json.loads(result["context"]).get("source_refs",[])),risk_flags=json.dumps(result["risks"]),reviewer_notes=result["technical_review"])
    db.add(draft); db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="workflow_completed",details=json.dumps({"agents":result.get("agent_trace",[]),"quality_score":result["quality_score"]}))); db.commit(); return serialize(job,True)
def serialize(job,detail=False):
    out={"id":job.id,"title":job.title,"content_type":job.content_type,"audience":job.audience,"product_area":job.product_area,"channel":job.channel,"status":job.status,"quality_score":job.quality_score,"created_at":job.created_at.isoformat()}
    if detail:
        drafts = sorted(job.drafts, key=lambda draft: draft.version)
        serialized_drafts = []
        for draft in drafts:
            try:
                technical_review = json.loads(draft.reviewer_notes or "{}")
            except json.JSONDecodeError:
                technical_review = {"notes": draft.reviewer_notes or ""}
            serialized_drafts.append({"id":draft.id,"version":draft.version,"content":draft.content,"final_document":draft.content,"stage":draft.stage,"source_refs":json.loads(draft.source_refs or "[]"),"risk_flags":json.loads(draft.risk_flags or "[]"),"reviewer_notes":draft.reviewer_notes,"technical_review":technical_review,"approved":draft.approved,"generated_at":technical_review.get("generated_at", draft.created_at.isoformat())})
        latest = serialized_drafts[-1] if serialized_drafts else None
        out.update({"source_text":job.source_text,"context_pack":job.context_pack,"quality_score":job.quality_score,"final_document":latest["final_document"] if latest else "","technical_review":latest["technical_review"] if latest else {},"drafts":serialized_drafts})
    return out
