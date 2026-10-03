"""Shared fixtures. Runs the real FastAPI app against a temp SQLite DB in mock-AI mode.

Firebase verification is replaced by a header (X-Test-Role) so tests need no cloud credentials.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
_tmp = tempfile.mkdtemp()
os.environ.update({
    "DATABASE_URL": f"sqlite:///{_tmp}/test.db",
    "AI_PROVIDER": "mock",
    "CHROMA_PERSIST_DIRECTORY": f"{_tmp}/chroma",
    "KNOWLEDGE_DATA_DIR": str(ROOT / "data"),
})
sys.path.insert(0, str(BACKEND))
os.chdir(_tmp)  # exports/ and data/uploads are written relative to the working dir

import pytest
from fastapi import Depends, HTTPException, Header
from fastapi.testclient import TestClient

from app.main import app
from app.auth.security import get_current_user
from app.db.session import SessionLocal, get_db
from app.models.entities import User

ROLES = ["writer", "writer2", "reviewer", "approver", "admin"]


def _override(x_test_role: str = Header(default=""), db=Depends(get_db)):
    if not x_test_role:
        raise HTTPException(401, "Authentication required")
    return db.query(User).filter_by(email=f"{x_test_role}@test.dev").one()


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_current_user] = _override
    with TestClient(app) as c:
        with SessionLocal() as db:
            for name in ROLES:
                db.add(User(email=f"{name}@test.dev", name=name, role=name.rstrip("2"), firebase_uid=f"uid-{name}"))
            db.commit()
        yield c
    app.dependency_overrides.clear()


def as_role(role):
    return {"X-Test-Role": role}


@pytest.fixture()
def hdr():
    return as_role


SAMPLE = (ROOT / "data" / "sample_inputs")


def read_sample(name):
    return (SAMPLE / name).read_text(encoding="utf-8")


@pytest.fixture()
def make_job(client):
    def _make(source=None, content_type="documentation", title="Widgets API update", role="writer"):
        body = {"title": title, "content_type": content_type, "audience": "Developers",
                "source_text": source or read_sample("api_change.txt")}
        r = client.post("/api/content-jobs", json=body, headers=as_role(role))
        assert r.status_code == 200, r.text
        return r.json()
    return _make


@pytest.fixture()
def run_job(client, make_job):
    def _run(**kw):
        job = make_job(**kw)
        r = client.post(f"/api/content-jobs/{job['id']}/run", headers=as_role(kw.get("role", "writer")))
        assert r.status_code == 200, r.text
        return r.json()
    return _run
