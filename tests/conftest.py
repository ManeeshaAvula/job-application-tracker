"""Pytest fixtures: run the API against a throwaway SQLite file."""

import os
import tempfile

# Point the app at a temp database BEFORE importing it.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def make_application(client, **overrides):
    payload = {
        "company": "Example Corp",
        "role_title": "Software Engineer",
        "location": "Austin, TX",
        "work_mode": "remote",
        "status": "applied",
    }
    payload.update(overrides)
    response = client.post("/applications", json=payload)
    assert response.status_code == 201, response.text
    return response.json()
