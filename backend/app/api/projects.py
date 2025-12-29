from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models import Export, Paper, Project
from schemas import ProjectCreate, ProjectOut, PaperOut, ExportOut
from workers.celery_app import run_pipeline_task

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = Project(
        user_id=current_user.id,
        topic=payload.topic,
        keywords=payload.keywords or [],
        config={
            "search": payload.search.dict(),
            "runtime": payload.runtime.dict(),
            "providers": payload.providers.dict(),
        },
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )


@router.get("/{project_id}", response_model=ProjectOut)
def project_detail(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"success": True}


@router.post("/{project_id}/run")
def run_pipeline(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    task = run_pipeline_task.delay(project.id)
    return {"task_id": task.id}


@router.get("/{project_id}/status")
def project_status(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": project.status, "stage": project.stage, "progress": project.progress}


@router.get("/{project_id}/papers", response_model=list[PaperOut])
def project_papers(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(Paper).filter(Paper.project_id == project.id).all()


@router.get("/{project_id}/exports", response_model=list[ExportOut])
def project_exports(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(Export).filter(Export.project_id == project.id).all()
