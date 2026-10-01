import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Draft, ContentJob, Review, AuditEvent
from app.auth.security import require_roles
router=APIRouter(prefix="/drafts",tags=["reviews"])
class ReviewIn(BaseModel): decision:str; comments:str=""
class RefineIn(BaseModel): comments:str=""
@router.post("/{draft_id}/review")
def review(draft_id:int,body:ReviewIn,db:Session=Depends(get_db),user=Depends(require_roles("reviewer","approver","admin"))):
    if body.decision not in {"approve","reject","request_revision"}: raise HTTPException(400,"Invalid decision")
    draft=db.get(Draft,draft_id)
    if not draft: raise HTTPException(404,"Draft not found")
    draft.approved=body.decision=="approve"
    job=db.get(ContentJob,draft.job_id); job.status="approved" if draft.approved else ("revision_requested" if body.decision=="request_revision" else "rejected")
    db.add(Review(draft_id=draft_id,reviewer_id=user.id,decision=body.decision,comments=body.comments))
    db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="review",details=json.dumps(body.model_dump())))
    db.commit(); return {"ok":True,"status":job.status,"approved":draft.approved}
@router.post("/{draft_id}/refine")
async def refine(draft_id:int,body:RefineIn,db:Session=Depends(get_db),user=Depends(require_roles("writer","reviewer","admin"))):
    draft=db.get(Draft,draft_id)
    if not draft: raise HTTPException(404,"Draft not found")
    job=db.get(ContentJob,draft.job_id)
    if user.role == "writer" and job.owner_id != user.id: raise HTTPException(403,"Writers can only refine their own drafts")
    from app.services.ai_provider import AIProvider
    from app.orchestration.workflow import TechnicalReviewerAgent, clean_markdown, document_metadata, fact_text, fact_sources
    instruction="Rewrite the document to address the reviewer feedback. Preserve all supported facts, do not add unsupported information, and return Markdown only."
    prompt=f"Reviewer feedback:\n{body.comments.strip() or 'Improve the document based on the requested revision.'}\n\nCurrent document:\n{draft.content}"
    ai=AIProvider()
    content=clean_markdown(await ai.generate(instruction,prompt))
    try:
        context=json.loads(job.context_pack or "{}")
    except json.JSONDecodeError:
        context={}
    technical=(await TechnicalReviewerAgent(ai).run(job,content,context)).output
    gaps=[str(value).strip() for value in context.get("gaps",[]) if str(value).strip()]
    unsupported=[str(value).strip() for value in technical.get("unsupported_claims",[]) if str(value).strip()]
    risks=[str(value).strip() for value in technical.get("risks",[]) if str(value).strip()]
    score=max(0,100-min(40,len(unsupported)*15)-min(25,len(risks)*10)-min(20,len(gaps)*3)-(10 if technical.get("verdict")!="PASS" else 0))
    job.quality_score=score
    metadata=document_metadata()
    technical_review={**technical,"supported_information":[{"fact":fact_text(item),"source_refs":fact_sources(item)} for item in context.get("facts",[]) if fact_text(item)],"context_gaps":gaps,"source_refs":json.loads(draft.source_refs or "[]"),"quality_score":score,"generated_at":metadata["iso"],"evidence_count":len(context.get("facts",[])),"human_approval_required":True}
    risk_flags=unsupported+risks+[f"Context gap: {gap}" for gap in gaps]
    new=Draft(job_id=job.id,version=max(item.version for item in job.drafts)+1,content=content,stage="publishing_preparation",source_refs=draft.source_refs,risk_flags=json.dumps(risk_flags),reviewer_notes=json.dumps(technical_review,indent=2))
    job.status="review"; db.add(new); db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="draft_refined",details=json.dumps({"from_version":draft.version,"feedback":body.comments}))); db.commit(); db.refresh(new)
    return {"draft_id":new.id,"version":new.version,"content":new.content}
