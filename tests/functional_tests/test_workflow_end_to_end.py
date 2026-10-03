from conftest import as_role


def test_full_flow_intake_to_export(client, run_job):
    job = run_job()
    assert job["status"] == "review" and job["drafts"]
    draft = job["drafts"][0]
    assert "Source references" in draft["content"]
    assert draft["technical_review"]["human_approval_required"] is True
    assert draft["technical_review"]["prompt_version"] == "v1"

    r = client.post(f"/api/drafts/{draft['id']}/review", json={"decision": "approve", "comments": "ok"}, headers=as_role("approver"))
    assert r.status_code == 200 and r.json()["approved"] is True

    md = client.post("/api/publish/export", json={"draft_id": draft["id"]}, headers=as_role("approver")).json()
    assert md["filename"].endswith(".md") and md["content"].startswith("---") and "approved_by: approver" in md["content"]

    cms = client.post("/api/publish/export", json={"draft_id": draft["id"], "format": "cms_json"}, headers=as_role("admin")).json()
    assert cms["filename"].endswith(".json") and '"body_markdown"' in cms["content"]


def test_context_pack_endpoint(client, make_job):
    job = make_job()
    r = client.post("/api/context-pack", json={"job_id": job["id"]}, headers=as_role("writer"))
    assert r.status_code == 200
    pack = r.json()["context_pack"]
    assert pack["facts"] and any("rate limit" in g.lower() for g in pack["gaps"])


def test_stage_rerun_edit_and_diff(client, run_job):
    job = run_job()
    d1 = job["drafts"][0]["id"]
    r = client.post(f"/api/drafts/{d1}/refine", json={"stage": "tone", "comments": "friendlier"}, headers=as_role("writer"))
    assert r.status_code == 200 and r.json()["version"] == 2
    e = client.post(f"/api/drafts/{r.json()['draft_id']}/edit", json={"content": "# Edited\n\nManual change"}, headers=as_role("reviewer"))
    assert e.status_code == 200 and e.json()["version"] == 3
    d = client.get(f"/api/drafts/{d1}/diff/{e.json()['draft_id']}", headers=as_role("reviewer"))
    assert d.status_code == 200 and "Edited" in d.json()["diff"]


def test_audit_log_and_metrics(client, run_job):
    job = run_job()
    audit = client.get(f"/api/content-jobs/{job['id']}/audit", headers=as_role("reviewer")).json()
    types = [a["event_type"] for a in audit]
    assert "job_created" in types and "workflow_completed" in types
    m = client.get("/api/metrics", headers=as_role("admin")).json()
    for key in ("total_jobs", "rework_rate", "avg_approval_hours", "error_rate", "pipeline"):
        assert key in m


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/health/ready").json()["status"] == "ready"
