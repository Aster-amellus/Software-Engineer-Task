import os
import sys

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/arxiv_review_test",
)
os.environ.setdefault("REDIS_URL", "memory://")
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")

app_dir = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(app_dir))

from db.base import Base  # noqa: E402
from db.session import engine  # noqa: E402
import models  # noqa: F401, E402

Base.metadata.create_all(bind=engine)

import pytest
from fastapi.testclient import TestClient
from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
