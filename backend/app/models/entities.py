from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    firebase_uid: Mapped[str | None] = mapped_column(String(128), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(30), default="writer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ContentJob(Base):
    __tablename__ = "content_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(60))
    audience: Mapped[str] = mapped_column(String(120))
    product_area: Mapped[str] = mapped_column(String(120), default="General")
    channel: Mapped[str] = mapped_column(String(120), default="Documentation")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(40), default="intake")
    source_text: Mapped[str] = mapped_column(Text)
    context_pack: Mapped[str] = mapped_column(Text, default="")
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    owner = relationship("User")
    drafts = relationship("Draft", back_populates="job", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="job", cascade="all, delete-orphan")

class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("content_jobs.id"))
    version: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(String(60), default="draft")
    source_refs: Mapped[str] = mapped_column(Text, default="[]")
    risk_flags: Mapped[str] = mapped_column(Text, default="[]")
    reviewer_notes: Mapped[str] = mapped_column(Text, default="")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    job = relationship("ContentJob", back_populates="drafts")

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(40))
    comments: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("content_jobs.id"))
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    job = relationship("ContentJob", back_populates="audit_events")
