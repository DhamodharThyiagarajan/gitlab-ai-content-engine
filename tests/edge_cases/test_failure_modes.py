from conftest import as_role, read_sample


def test_source_too_short_rejected_at_intake(client):
    r = client.post("/api/content-jobs", json={"title": "abc", "content_type": "documentation", "audience": "Dev", "source_text": "hi"}, headers=as_role("writer"))
    assert r.status_code == 422


def test_thin_context_fails_visibly_and_safely(client, make_job):
    job = make_job(source="....... ??? ....... ???", title="Thin source")
    r = client.post(f"/api/content-jobs/{job['id']}/run", headers=as_role("writer"))
    assert r.status_code == 422 and "Insufficient context" in r.json()["detail"]
    assert client.get(f"/api/content-jobs/{job['id']}", headers=as_role("writer")).json()["status"] == "failed"


def test_upload_rejects_empty_and_unsupported(client):
    f = lambda name, data: client.post("/api/content-jobs/upload", data={"title": "Upload test"}, files={"file": (name, data)}, headers=as_role("writer"))
    assert f("a.txt", b"").status_code == 400
    assert f("a.exe", b"binary").status_code == 400


def test_upload_txt_creates_job_with_source_markers(client):
    r = client.post("/api/content-jobs/upload", data={"title": "Upload ok"}, files={"file": ("notes.txt", b"GitLab 17.5 adds feature X for runners.")}, headers=as_role("writer"))
    assert r.status_code == 200 and "[SOURCE: notes.txt" in r.json()["source_text"]


def test_invalid_review_decision_and_stage(client, run_job):
    d = run_job()["drafts"][0]["id"]
    assert client.post(f"/api/drafts/{d}/review", json={"decision": "maybe"}, headers=as_role("approver")).status_code == 400
    assert client.post(f"/api/drafts/{d}/refine", json={"stage": "nonsense"}, headers=as_role("writer")).status_code == 400


def test_unknown_job_404(client):
    assert client.get("/api/content-jobs/99999", headers=as_role("admin")).status_code == 404


def test_conflicting_notes_still_produce_reviewable_draft(client, run_job):
    job = run_job(source=read_sample("conflicting_notes.txt"), title="Export limits")
    assert job["status"] == "review"  # human review resolves the conflict; nothing auto-publishes
