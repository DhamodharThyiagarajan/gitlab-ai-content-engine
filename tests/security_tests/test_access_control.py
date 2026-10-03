from conftest import as_role


def test_unauthenticated_is_rejected(client):
    assert client.get("/api/content-jobs").status_code == 401


def test_writer_cannot_approve_or_export(client, run_job):
    d = run_job()["drafts"][0]["id"]
    assert client.post(f"/api/drafts/{d}/review", json={"decision": "approve"}, headers=as_role("writer")).status_code == 403
    assert client.post("/api/publish/export", json={"draft_id": d}, headers=as_role("writer")).status_code == 403


def test_reviewer_cannot_approve_but_can_request_revision(client, run_job):
    d = run_job()["drafts"][0]["id"]
    assert client.post(f"/api/drafts/{d}/review", json={"decision": "approve"}, headers=as_role("reviewer")).status_code == 403
    assert client.post(f"/api/drafts/{d}/review", json={"decision": "request_revision", "comments": "fix"}, headers=as_role("reviewer")).status_code == 200


def test_export_blocked_until_approved(client, run_job):
    d = run_job()["drafts"][0]["id"]
    r = client.post("/api/publish/export", json={"draft_id": d}, headers=as_role("approver"))
    assert r.status_code == 409


def test_writer_cannot_read_other_writers_job(client, make_job):
    job = make_job(role="writer")
    assert client.get(f"/api/content-jobs/{job['id']}", headers=as_role("writer2")).status_code == 403
    assert client.get(f"/api/content-jobs/{job['id']}", headers=as_role("reviewer")).status_code == 200


def test_client_cannot_self_promote_role(client):
    r = client.put("/api/auth/profile", json={"role": "admin", "displayName": "x"}, headers=as_role("writer"))
    assert r.status_code == 200 and r.json()["user"]["role"] == "writer"


def test_only_admin_lists_users_and_sets_roles(client):
    assert client.get("/api/auth/users", headers=as_role("writer")).status_code == 403
    assert client.get("/api/auth/users", headers=as_role("admin")).status_code == 200
