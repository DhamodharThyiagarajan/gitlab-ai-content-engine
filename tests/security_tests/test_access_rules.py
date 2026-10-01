from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.api.auth import ProfileUpdate


def test_security_and_governance_docs_exist():
    root = Path(__file__).resolve().parents[2]
    assert (root / "docs" / "architecture.md").exists()
    assert (root / "backend" / "auth" / "README.md").exists()
    assert (root / "deployment" / "environment_setup.md").exists()


def test_profile_update_rejects_client_supplied_role():
    with pytest.raises(ValidationError):
        ProfileUpdate.model_validate({"role": "admin"})
