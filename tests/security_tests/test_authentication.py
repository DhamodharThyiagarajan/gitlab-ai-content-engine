
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_content_jobs_requires_authentication():
    response = client.get("/api/content-jobs")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_create_content_job_requires_authentication():
    response = client.post(
        "/api/content-jobs",
        json={
            "title": "Security Test",
            "content_type": "documentation",
            "audience": "developers",
            "product_area": "Testing",
            "channel": "Documentation",
            "source_text": "Authentication security test",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_metrics_requires_authentication():
    response = client.get("/api/metrics")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_publish_requires_authentication():
    response = client.post(
        "/api/publish/export",
        json={"draft_id": 999999},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
