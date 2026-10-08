from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.entities import User, ContentJob, Draft
from app.db.session import Base, engine


Base.metadata.create_all(bind=engine)

client = TestClient(app)


def create_test_data(approved=True):
    db = SessionLocal()

    user = User(
        email="publishing_test@example.com",
        firebase_uid=None,
        name="Publishing Test User",
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    job = ContentJob(
        title="Publishing Test",
        content_type="documentation",
        audience="developers",
        product_area="Testing",
        channel="Documentation",
        owner_id=user.id,
        status="review",
        source_text="Test source content",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    draft = Draft(
        job_id=job.id,
        version=1,
        content="# Publishing Test\n\nTest content.",
        stage="review",
        approved=approved,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    draft_id = draft.id
    job_id = job.id

    db.close()

    return draft_id, job_id


def cleanup_test_data(job_id):
    db = SessionLocal()

    job = db.get(ContentJob, job_id)

    if job:
        db.delete(job)

    user = db.query(User).filter(
        User.email == "publishing_test@example.com"
    ).first()

    if user:
        db.delete(user)

    db.commit()
    db.close()

    for path in Path("exports").glob(f"{job_id}-*"):
        if path.exists():
            path.unlink()


def test_export_approved_draft():
    draft_id, job_id = create_test_data(approved=True)

    try:
        # Directly call the endpoint function with a test admin user.
        from backend.app.api.publishing import export

        db = SessionLocal()
        user = db.query(User).filter(
            User.email == "publishing_test@example.com"
        ).first()

        result = export(
            body=type("ExportIn", (), {"draft_id": draft_id})(),
            db=db,
            user=user,
        )

        assert result["status"] == "published"
        assert result["content"] == "# Publishing Test\n\nTest content."

        exported_file = Path(result["path"])
        assert exported_file.exists()
        assert exported_file.read_text(encoding="utf-8") == result["content"]

        db.close()

    finally:
        cleanup_test_data(job_id)


def test_export_unapproved_draft():
    draft_id, job_id = create_test_data(approved=False)

    try:
        from app.api.publishing import export
        from fastapi import HTTPException

        db = SessionLocal()
        user = db.query(User).filter(
            User.email == "publishing_test@example.com"
        ).first()

        try:
            export(
                body=type("ExportIn", (), {"draft_id": draft_id})(),
                db=db,
                user=user,
            )
            assert False, "Expected HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 409
            assert exc.detail == "Draft must be approved before export"

        db.close()

    finally:
        cleanup_test_data(job_id)


def test_export_missing_draft():
    from backend.app.api.publishing import export
    from fastapi import HTTPException

    db = SessionLocal()

    user = User(
        email="publishing_missing@example.com",
        firebase_uid=None,
        name="Publishing Missing Test",
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        try:
            export(
                body=type("ExportIn", (), {"draft_id": 999999})(),
                db=db,
                user=user,
            )
            assert False, "Expected HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 404
            assert exc.detail == "Draft not found"

    finally:
        db.delete(user)
        db.commit()
        db.close()