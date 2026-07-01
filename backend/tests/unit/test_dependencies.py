from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.dependencies import get_current_user
from app.models import User


def test_bypass_requires_x_user_id_header():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization=None, x_user_id=None, db=db)
    assert exc_info.value.status_code == 401


def test_bypass_rejects_unknown_user():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization=None, x_user_id="unknown-id", db=db)
    assert exc_info.value.status_code == 401


def test_bypass_resolves_existing_user():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = User(id="abc-123")
    result = get_current_user(authorization=None, x_user_id="abc-123", db=db)
    assert result == "abc-123"
