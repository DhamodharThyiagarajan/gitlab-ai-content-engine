
from pathlib import Path

from app.api.publishing import export
from app.db.session import Base, SessionLocal, engine
from app.models.entities import ContentJob, Draft, User


Base.metadata.create_all(bind=engine)


def test_export_handles_special_characters_in_title():
    db = SessionLocal()

    try:
        user = User(
            email="edge_case_publish@example.com",
            name="Edge Case User",
            role="admin",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        job = ContentJob(
            title="API / Testing: Version 2.0!",
            content_type="documentation",
            audience="developers",
            product_area="Testing",
            channel="Documentation",
            owner_id=user.id,
            status="review",
            source_text="Edge case source",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        draft = Draft(
            job_id=job.id,
            version=1,
            content="# Test Content",
            approved=True,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

        result = export(
            body=type("ExportBody", (), {"draft_id": draft.id})(),
            db=db,
            user=user,
        )

        filename = result["filename"]

        assert result["status"] == "published"
        assert filename.endswith(".md")
        assert "/" not in filename
        assert ":" not in filename
        assert "!" not in filename
        assert Path(result["path"]).exists()

        Path(result["path"]).unlink(missing_ok=True)

    finally:
        job = locals().get("job")
        user = locals().get("user")

        if job:
            db.delete(job)

        if user:
            db.delete(user)

        db.commit()
        db.close()
