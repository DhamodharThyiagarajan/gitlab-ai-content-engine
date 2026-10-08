
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.auth.security import require_roles


def test_writer_role_is_allowed_for_writer_endpoint():
    user = SimpleNamespace(role="writer")

    checker = require_roles("writer", "admin")

    result = checker(user)

    assert result == user


def test_admin_role_is_allowed_for_writer_endpoint():
    user = SimpleNamespace(role="admin")

    checker = require_roles("writer", "admin")

    result = checker(user)

    assert result == user


def test_writer_role_is_rejected_from_reviewer_endpoint():
    user = SimpleNamespace(role="writer")

    checker = require_roles("reviewer", "approver", "admin")

    with pytest.raises(HTTPException) as exc_info:
        checker(user)

    assert exc_info.value.status_code == 403


def test_reviewer_role_is_rejected_from_admin_only_endpoint():
    user = SimpleNamespace(role="reviewer")

    checker = require_roles("admin")

    with pytest.raises(HTTPException) as exc_info:
        checker(user)

    assert exc_info.value.status_code == 403
