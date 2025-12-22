import os
import sys
from importlib import reload
from pathlib import Path
import importlib

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))

try:
    importlib.import_module("sqlalchemy")
except ImportError:  # pragma: no cover - dependency missing in offline env
    pytest.skip("sqlalchemy not installed", allow_module_level=True)

# Configure test env before imports
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./test.db"
os.environ["STORAGE_ROOT"] = str(Path("./tmp_storage").resolve())
os.environ["CHROMA_DIR"] = str(Path("./tmp_chroma").resolve())

from core import config as core_config
reload(core_config)

from db import session as db_session
reload(db_session)

from db.base import Base
from models import Analysis, Export, Paper, Project, User
from services.pipeline import PipelineService


def setup_module(module):
    # ensure clean filesystem
    storage_root = Path(os.environ["STORAGE_ROOT"])
    chroma_dir = Path(os.environ["CHROMA_DIR"])
    storage_root.mkdir(parents=True, exist_ok=True)
    chroma_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=db_session.engine)


def teardown_module(module):
    Path("./test.db").unlink(missing_ok=True)


def test_pipeline_run_creates_exports():
    db = db_session.SessionLocal()
    user = User(email="test@example.com", password_hash="x")
    db.add(user)
    db.commit()
    db.refresh(user)

    project = Project(
        user_id=user.id,
        topic="Test Topic",
        keywords=["ai"],
        config={
            "search": {"max_results": 2, "start": 0, "sortBy": "submittedDate", "sortOrder": "descending"},
            "runtime": {"top_k": 1, "max_papers": 2},
            "providers": {"llm": {"name": "mock"}},
        },
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    service = PipelineService(db)
    service.run(project)
    db.refresh(project)

    exports = db.query(Export).filter(Export.project_id == project.id).all()
    analyses = db.query(Analysis).filter(Analysis.project_id == project.id).all()
    papers = db.query(Paper).filter(Paper.project_id == project.id).all()

    assert project.status == "completed"
    assert len(exports) >= 1
    assert len(analyses) == 1
    assert papers[0].local_path is not None
    for export in exports:
        assert Path(export.local_path).exists()

    db.close()
