"""Isolated configuration shared by the API tests."""
import os
import tempfile
from pathlib import Path


_test_db_dir = tempfile.mkdtemp(prefix="ad-backend-tests-")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{Path(_test_db_dir) / 'test.db'}")
os.environ.setdefault("JWT_SECRET", "test-only-secret-that-is-long-enough-for-hmac")
os.environ.setdefault("DEVICE_SECRET_SALT", "test-only-device-secret-salt-long-enough")
os.environ.setdefault("DEVICE_CLAIM_KEY", "test-only-claim-key-long-enough-for-hmac")
os.environ.setdefault("RATE_LIMIT_DB_PATH", f"{_test_db_dir}/rate-limits.sqlite")

from app.db.base import Base
from app.db.session import engine
from app.models import device, measurement, password_reset, push_subscription, user

Base.metadata.create_all(bind=engine)


import pytest
from app.api.v1 import auth as auth_router


@pytest.fixture(autouse=True)
def _isolate_rate_limiter():
    """Reset the rate-limiter between tests so hits don't leak across tests."""
    if auth_router._limiter is not None:
        auth_router._limiter.reset()
    yield
