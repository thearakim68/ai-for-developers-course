"""Shared test setup: every test gets a brand-new in-memory database with the demo data."""
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.clock import get_now
from app.main import create_app
from seed import seed_database

# Tests never read the real clock: "now" is always this moment.
FIXED_NOW = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)

ANA = {"Authorization": "Bearer ana-token"}
BEN = {"Authorization": "Bearer ben-token"}
ADMIN = {"Authorization": "Bearer admin-token"}


@pytest.fixture
def app():
    app = create_app("sqlite://")  # private in-memory database
    with app.state.session_factory() as db:
        seed_database(db)
        db.commit()
    app.dependency_overrides[get_now] = lambda: FIXED_NOW
    yield app
    app.state.engine.dispose()


@pytest.fixture
def client(app):
    return TestClient(app)
