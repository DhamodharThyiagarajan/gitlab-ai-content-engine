import json
import difflib
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Draft, ContentJob, Review, AuditEvent
from app.auth.security import require_roles, get_current_user
router=APIRouter(prefix="/drafts",tags=["reviews"])
class ReviewIn(BaseModel): decision:str; comments:str=""
STAGE_INSTRUCTIONS={
    "full":"Address the reviewer feedback.",
    "tone":"Rerun only the TONE stage: adjust voice and audience fit per the GitLab voice guide. Do not change any facts.",
    "structure":"Rerun only the STRUCTURE stage: improve headings, ordering and scannability. Do not change any facts.",
    "clarity":"Rerun only the CLARITY stage: shorten and simplify sentences. Do not change any facts.",
    "technical":"Rerun the TECHNICAL stage: remove or soften any claim that is not supported by the source material.",
}
class RefineIn(BaseModel):
    comments:str=""
    stage:str="full"
class EditIn(BaseModel): content:str; comments:str=""
@router.post("/{draft_id}/review")
def review(draft_id:int,body:ReviewIn,db:Session=Depends(get_db),user=Depends(require_roles("reviewer","approver","admin"))):
    if body.decision not in {"approve","reject","request_revision"}: raise HTTPException(400,"Invalid decision")
    if body.decision=="approve" and user.role not in {"approver","admin"}: raise HTTPException(403,"Only approvers or admins can approve a draft")
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
    from ai.agents.technical_reviewer.agent import TechnicalReviewerAgent
    from ai.common import clean_markdown, document_metadata, fact_text, fact_sources, clean_review_items, clean_source_refs, normalize_review_payload
    if body.stage not in STAGE_INSTRUCTIONS: raise HTTPException(400,f"Invalid stage. Use one of: {', '.join(STAGE_INSTRUCTIONS)}")
    from ai.prompts import style_guidance, PROMPT_VERSION
    instruction=STAGE_INSTRUCTIONS[body.stage]+" Preserve all supported facts, do not add unsupported information, and return Markdown only.\n\n"+style_guidance(job.content_type)
    prompt=f"Reviewer feedback:\n{body.comments.strip() or 'Improve the document based on the requested revision.'}\n\nCurrent document:\n{draft.content}"
    ai=AIProvider()
    content=clean_markdown(await ai.generate(instruction,prompt))
    try:
        context=json.loads(job.context_pack or "{}")
    except json.JSONDecodeError:
        context={}
    technical=(await TechnicalReviewerAgent(ai).run(job,content,context)).output
    gaps=clean_review_items(context.get("gaps",[]))
    unsupported=clean_review_items(technical.get("unsupported_claims",[]))
    risks=clean_review_items(technical.get("risks",[]))
    score=max(0,100-min(40,len(unsupported)*15)-min(25,len(risks)*10)-min(20,len(gaps)*3)-(10 if technical.get("verdict")!="PASS" else 0))
    job.quality_score=score
    metadata=document_metadata()
    technical_review=normalize_review_payload({
        **technical,
        "supported_information": [{"fact": fact_text(item), "source_refs": clean_source_refs(fact_sources(item))} for item in context.get("facts", []) if fact_text(item)],
        "context_gaps": gaps,
        "source_refs": clean_source_refs(json.loads(draft.source_refs or "[]")),
        "quality_score": score,
        "generated_at": metadata["iso"],
        "evidence_count": len(context.get("facts", [])),
        "human_approval_required": True,
    }, fallback_source_refs=json.loads(draft.source_refs or "[]"))
    from ai.common import ungrounded_claims
    for claim in ungrounded_claims(content,job.source_text or ""):
        if claim not in unsupported: unsupported.append(claim)
    technical_review["unsupported_claims"]=unsupported; technical_review["prompt_version"]=PROMPT_VERSION; technical_review["refine_stage"]=body.stage
    risk_flags=unsupported+risks+[f"Context gap: {gap}" for gap in gaps]
    new=Draft(job_id=job.id,version=max(item.version for item in job.drafts)+1,content=content,stage="publishing_preparation",source_refs=draft.source_refs,risk_flags=json.dumps(risk_flags),reviewer_notes=json.dumps(technical_review,indent=2))
    job.status="review"; db.add(new); db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="draft_refined",details=json.dumps({"from_version":draft.version,"feedback":body.comments,"stage":body.stage,"prompt_version":PROMPT_VERSION}))); db.commit(); db.refresh(new)
    return {"draft_id":new.id,"version":new.version,"content":new.content}


def _job_for(draft,db,user):
    job=db.get(ContentJob,draft.job_id)
    if user.role=="writer" and job.owner_id!=user.id: raise HTTPException(403,"Writers can only access their own drafts")
    return job

@router.post("/{draft_id}/edit")
def edit(draft_id:int,body:EditIn,db:Session=Depends(get_db),user=Depends(require_roles("writer","reviewer","admin"))):
    """Human edit: saved as a new version so nothing is overwritten and the approval gate restarts."""
    draft=db.get(Draft,draft_id)
    if not draft: raise HTTPException(404,"Draft not found")
    job=_job_for(draft,db,user)
    if not body.content.strip(): raise HTTPException(400,"Content cannot be empty")
    from ai.common import ungrounded_claims
    flags=[f for f in json.loads(draft.risk_flags or "[]") if not f.startswith("Not found in source material")]+ungrounded_claims(body.content,job.source_text or "")
    new=Draft(job_id=job.id,version=max(d.version for d in job.drafts)+1,content=body.content,stage="human_edit",source_refs=draft.source_refs,risk_flags=json.dumps(flags),reviewer_notes=draft.reviewer_notes)
    job.status="review"; db.add(new)
    db.add(AuditEvent(job_id=job.id,actor_id=user.id,event_type="draft_edited",details=json.dumps({"from_version":draft.version,"comments":body.comments})))
    db.commit(); db.refresh(new)
    return {"draft_id":new.id,"version":new.version,"risk_flags":flags}

@router.get("/{draft_id}/diff/{other_id}")
def diff(draft_id:int,other_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    a,b=db.get(Draft,draft_id),db.get(Draft,other_id)
    if not a or not b or a.job_id!=b.job_id: raise HTTPException(404,"Drafts not found or not from the same job")
    _job_for(a,db,user)
    text="\n".join(difflib.unified_diff(a.content.splitlines(),b.content.splitlines(),f"v{a.version}",f"v{b.version}",lineterm=""))
    return {"from_version":a.version,"to_version":b.version,"diff":text}
