import os
import sys
from importlib import reload
from pathlib import Path

import pytest
import importlib

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))

try:
    importlib.import_module("sqlalchemy")
except ImportError:  # pragma: no cover
    pytest.skip("sqlalchemy not installed", allow_module_level=True)

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./api_test.db"
os.environ["STORAGE_ROOT"] = str(Path("./tmp_storage_api").resolve())
os.environ["CHROMA_DIR"] = str(Path("./tmp_chroma_api").resolve())

from core import config as core_config
reload(core_config)
from db import session as db_session
reload(db_session)
from db.base import Base
import models  # noqa: F401 ensures models register tables
try:
    from fastapi.testclient import TestClient
    from app import main
except ImportError:  # pragma: no cover - fastapi unavailable in minimal envs
    pytest.skip("fastapi not installed", allow_module_level=True)

Base.metadata.create_all(bind=db_session.engine)
client = TestClient(main.app)


def test_register_login_and_create_project():
    resp = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "pass"})
    assert resp.status_code == 200

    token_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "user@example.com", "password": "pass", "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]

    proj_resp = client.post(
        "/api/v1/projects",
        json={"topic": "API Test", "keywords": ["api"], "search": {}, "runtime": {}, "providers": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert proj_resp.status_code == 200
    project_id = proj_resp.json()["id"]

    list_resp = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert list_resp.status_code == 200
    assert any(p["id"] == project_id for p in list_resp.json())
