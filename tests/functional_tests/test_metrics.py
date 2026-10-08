from datetime import datetime, timezone

from app.db.session import SessionLocal, Base, engine
from app.models.entities import User, ContentJob
from app.api.metrics import metrics


Base.metadata.create_all(bind=engine)


def create_user(db, email, name, role="writer"):
    user = User(
        email=email,
        firebase_uid=None,
        name=name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_job(
    db,
    owner_id,
    title,
    status,
    quality_score=0.0,
    created_at=None,
):
    job = ContentJob(
        title=title,
        content_type="documentation",
        audience="developers",
        product_area="Testing",
        channel="Documentation",
        owner_id=owner_id,
        status=status,
        source_text="Test source content",
        quality_score=quality_score,
    )

    if created_at:
        job.created_at = created_at
        job.updated_at = created_at

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def cleanup(db):
    db.query(ContentJob).delete()
    db.query(User).delete()
    db.commit()


def test_metrics_empty_database():
    db = SessionLocal()

    try:
        cleanup(db)

        user = create_user(
            db,
            "metrics_empty@example.com",
            "Metrics Empty User",
        )

        result = metrics(db=db, user=user)

        assert result["total_jobs"] == 0
        assert result["drafts"] == 0
        assert result["review_jobs"] == 0
        assert result["published_jobs"] == 0
        assert result["average_quality"] == 0.0
        assert all(item["jobs"] == 0 for item in result["trend"])
        assert all(item["value"] == 0 for item in result["pipeline"])
        assert result["recent_jobs"] == []

    finally:
        cleanup(db)
        db.close()


def test_metrics_actual_jobs():
    db = SessionLocal()

    try:
        cleanup(db)

        user = create_user(
            db,
            "metrics_actual@example.com",
            "Metrics Test User",
        )

        create_job(
            db,
            user.id,
            "Intake Job",
            "intake",
            0,
        )

        create_job(
            db,
            user.id,
            "Review Job",
            "review",
            80,
        )

        create_job(
            db,
            user.id,
            "Published Job",
            "published",
            90,
        )

        result = metrics(db=db, user=user)

        assert result["total_jobs"] == 3
        assert result["drafts"] == 0
        assert result["review_jobs"] == 1
        assert result["published_jobs"] == 1
        assert result["average_quality"] == 85.0

        pipeline = {
            item["name"]: item["value"]
            for item in result["pipeline"]
        }

        assert pipeline["Intake"] == 1
        assert pipeline["Review"] == 1
        assert pipeline["Publish"] == 1

        assert len(result["recent_jobs"]) == 3

    finally:
        cleanup(db)
        db.close()


def test_metrics_writer_filtering():
    db = SessionLocal()

    try:
        cleanup(db)

        writer_a = create_user(
            db,
            "writer_a@example.com",
            "Writer A",
            "writer",
        )

        writer_b = create_user(
            db,
            "writer_b@example.com",
            "Writer B",
            "writer",
        )

        create_job(
            db,
            writer_a.id,
            "Writer A Review",
            "review",
            80,
        )

        create_job(
            db,
            writer_a.id,
            "Writer A Published",
            "published",
            90,
        )

        create_job(
            db,
            writer_b.id,
            "Writer B Published",
            "published",
            100,
        )

        result = metrics(db=db, user=writer_a)

        assert result["total_jobs"] == 2
        assert result["review_jobs"] == 1
        assert result["published_jobs"] == 1
        assert result["average_quality"] == 85.0

        titles = [
            job["title"]
            for job in result["recent_jobs"]
        ]

        assert "Writer A Review" in titles
        assert "Writer A Published" in titles
        assert "Writer B Published" not in titles

    finally:
        cleanup(db)
        db.close()


def test_metrics_monthly_trend():
    db = SessionLocal()

    try:
        cleanup(db)

        user = create_user(
            db,
            "metrics_trend@example.com",
            "Metrics Trend User",
        )

        september = datetime(
            2026,
            9,
            15,
            tzinfo=timezone.utc,
        )

        october_1 = datetime(
            2026,
            10,
            1,
            tzinfo=timezone.utc,
        )

        october_2 = datetime(
            2026,
            10,
            5,
            tzinfo=timezone.utc,
        )

        create_job(
            db,
            user.id,
            "September Job",
            "review",
            80,
            september,
        )

        create_job(
            db,
            user.id,
            "October Job 1",
            "intake",
            0,
            october_1,
        )

        create_job(
            db,
            user.id,
            "October Job 2",
            "review",
            90,
            october_2,
        )

        result = metrics(db=db, user=user)

        trend = {
            item["month"]: item["jobs"]
            for item in result["trend"]
        }

        assert trend["Sep"] == 1
        assert trend["Oct"] == 2

    finally:
        cleanup(db)
        db.close()