from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.entities import ContentJob, Draft, AuditEvent, Review
from app.auth.security import require_roles
router=APIRouter(prefix="/metrics",tags=["metrics"])
@router.get("")
def metrics(db:Session=Depends(get_db),user=Depends(require_roles("writer","reviewer","approver","admin"))):
    jobs_query=db.query(ContentJob)
    if user.role == "writer":
        jobs_query=jobs_query.filter(ContentJob.owner_id==user.id)

    status_rows=jobs_query.with_entities(ContentJob.status,func.count(ContentJob.id)).group_by(ContentJob.status).all()
    status_counts={status:count for status,count in status_rows}
    total=sum(status_counts.values())
    job_ids=jobs_query.with_entities(ContentJob.id).subquery()
    draft_count=db.query(func.count(Draft.id)).filter(Draft.job_id.in_(job_ids)).scalar() or 0
    quality_query=db.query(func.avg(ContentJob.quality_score)).filter(ContentJob.quality_score>0)
    if user.role == "writer":
        quality_query=quality_query.filter(ContentJob.owner_id==user.id)
    average_quality=quality_query.scalar() or 0

    now=datetime.now(timezone.utc)
    month_starts=[]
    year,month=now.year,now.month
    for _ in range(7):
        month_starts.append(datetime(year,month,1,tzinfo=timezone.utc))
        year,month=(year-1,12) if month==1 else (year,month-1)
    month_starts.reverse()
    trend_query=jobs_query.filter(ContentJob.created_at>=month_starts[0]).with_entities(ContentJob.created_at).all()
    monthly_counts={start.strftime("%Y-%m"):0 for start in month_starts}
    for (created_at,) in trend_query:
        if created_at.tzinfo is None:
            created_at=created_at.replace(tzinfo=timezone.utc)
        key=created_at.strftime("%Y-%m")
        if key in monthly_counts:
            monthly_counts[key]+=1
    trend=[{"month":start.strftime("%b"),"jobs":monthly_counts[start.strftime("%Y-%m")]} for start in month_starts]
    recent=jobs_query.order_by(ContentJob.created_at.desc()).limit(5).all()
    pipeline=[
        {"name":"Intake","value":status_counts.get("intake",0)},
        {"name":"Context","value":status_counts.get("context_preparation",0)},
        {"name":"Draft","value":draft_count},
        {"name":"Refine","value":status_counts.get("refining",0)},
        {"name":"Review","value":status_counts.get("review",0)+status_counts.get("revision_requested",0)},
        {"name":"Publish","value":status_counts.get("approved",0)+status_counts.get("publish_ready",0)+status_counts.get("published",0)},
    ]
    # Operations signals from the spec: rework, approval cycle time, error rate, reviewer issue categories.
    job_id_list=[row[0] for row in jobs_query.with_entities(ContentJob.id).all()]
    per_job=dict(db.query(Draft.job_id,func.count(Draft.id)).filter(Draft.job_id.in_(job_id_list)).group_by(Draft.job_id).all()) if job_id_list else {}
    reworked=sum(1 for n in per_job.values() if n>1)
    rework_rate=round(100*reworked/len(per_job),1) if per_job else 0
    cycle_hours=[]
    if job_id_list:
        events=db.query(AuditEvent).filter(AuditEvent.job_id.in_(job_id_list),AuditEvent.event_type.in_(["workflow_completed","review"])).order_by(AuditEvent.id).all()
        first_done={}
        for e in events:
            ts=e.created_at if e.created_at.tzinfo else e.created_at.replace(tzinfo=timezone.utc)
            if e.event_type=="workflow_completed": first_done.setdefault(e.job_id,ts)
            elif e.event_type=="review" and '"approve"' in (e.details or "") and e.job_id in first_done:
                cycle_hours.append((ts-first_done.pop(e.job_id)).total_seconds()/3600)
    decisions=dict(db.query(Review.decision,func.count(Review.id)).group_by(Review.decision).all()) if user.role!="writer" else {}
    failed=status_counts.get("failed",0)
    return {
        "rework_rate":rework_rate,
        "avg_approval_hours":round(sum(cycle_hours)/len(cycle_hours),2) if cycle_hours else 0,
        "error_rate":round(100*failed/total,1) if total else 0,
        "review_decisions":decisions,
        "total_jobs":total,
        "drafts":draft_count,
        "review_jobs":status_counts.get("review",0)+status_counts.get("revision_requested",0),
        "published_jobs":status_counts.get("published",0),
        "average_quality":round(float(average_quality),1),
        "trend":trend,
        "pipeline":pipeline,
        "recent_jobs":[
            {"id":job.id,"title":job.title,"content_type":job.content_type,"status":job.status,"updated_at":job.updated_at.isoformat(),"owner":job.owner.name}
            for job in recent
        ],
    }
