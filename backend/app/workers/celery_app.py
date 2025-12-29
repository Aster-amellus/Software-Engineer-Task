from celery import Celery
from sqlalchemy.orm import Session

from core.config import get_settings
from db.session import SessionLocal
from models import Project
from services.pipeline import PipelineService
from utils.files import ensure_storage_dirs

settings = get_settings()
broker_url = settings.redis_url if not settings.task_always_eager else "memory://"
backend_url = settings.redis_url if not settings.task_always_eager else "cache+memory://"
celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url,
)
celery_app.conf.task_always_eager = settings.task_always_eager
celery_app.conf.task_store_eager_result = settings.task_always_eager


@celery_app.task(name="pipeline.run")
def run_pipeline_task(project_id: int):
    ensure_storage_dirs()
    db: Session = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return "project not found"
        service = PipelineService(db)
        service.run(project)
    finally:
        db.close()
    return "ok"
