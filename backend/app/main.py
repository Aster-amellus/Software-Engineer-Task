from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import auth, projects, ws
from utils.files import ensure_storage_dirs

app = FastAPI(title="Arxiv Review System", openapi_url="/api/v1/openapi.json")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")

# Mount the repository-level frontend directory to serve the minimal UI.
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")


@app.on_event("startup")
async def startup_event():
    ensure_storage_dirs()
