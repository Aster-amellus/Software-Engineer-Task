import os
from pathlib import Path

from core.config import get_settings

settings = get_settings()


def ensure_storage_dirs():
    Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)


def project_storage_path(project_id: int) -> str:
    path = Path(settings.storage_root) / f"project_{project_id}"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)
