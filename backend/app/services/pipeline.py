from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from infrastructure.arxiv import ArxivAdapter, MockArxivAdapter
from infrastructure.llm import LLMProvider, MockLLMProvider
from infrastructure.embedding import EmbeddingProvider, MockEmbeddingProvider
from infrastructure.pubsub import publish_project_event
from models import Analysis, Export, Paper, Project
from utils.files import project_storage_path

STAGES = [
    "KEYWORD_EXPAND",
    "ARXIV_SEARCH",
    "DEDUP",
    "TOPK_SELECT",
    "DOWNLOAD",
    "PARSE",
    "CHUNK",
    "EMBED",
    "RETRIEVE",
    "EXTRACT",
    "WRITE",
    "EXPORT",
    "DONE",
]


class PipelineService:
    def __init__(
        self,
        db: Session,
        arxiv_adapter: ArxivAdapter | None = None,
        llm_provider: LLMProvider | None = None,
        embed_provider: EmbeddingProvider | None = None,
    ):
        self.db = db
        self.arxiv = arxiv_adapter or MockArxivAdapter()
        self.llm = llm_provider or MockLLMProvider()
        self.embed = embed_provider or MockEmbeddingProvider()

    def _update_stage(self, project: Project, stage: str, progress: int):
        project.stage = stage
        project.progress = progress
        project.updated_at = datetime.utcnow()
        self.db.add(project)
        self.db.commit()
        publish_project_event(project.id, "stage", {"stage": stage, "progress": progress})

    def run(self, project: Project):
        project.status = "running"
        self.db.commit()
        # KEYWORD_EXPAND (mock)
        self._update_stage(project, "KEYWORD_EXPAND", 5)
        keywords = project.keywords or []

        # ARXIV_SEARCH
        self._update_stage(project, "ARXIV_SEARCH", 10)
        search_cfg = (project.config or {}).get("search", {})
        results = self.arxiv.search(project.topic, search_cfg.get("start", 0), search_cfg.get("max_results", 5))

        # DEDUP + persist papers
        self._update_stage(project, "DEDUP", 20)
        self._materialize_papers(project, results)

        # TOPK_SELECT (mock select first N)
        self._update_stage(project, "TOPK_SELECT", 30)

        # DOWNLOAD/PARSE/CHUNK/EMBED/RETRIEVE
        self._update_stage(project, "DOWNLOAD", 40)
        self._update_stage(project, "PARSE", 50)
        self._update_stage(project, "CHUNK", 60)
        self._update_stage(project, "EMBED", 70)
        self._update_stage(project, "RETRIEVE", 75)

        # EXTRACT
        self._update_stage(project, "EXTRACT", 85)
        for paper in project.papers:
            extracted = self.llm.generate_structured(paper.abstract or "", schema={})
            analysis = Analysis(
                project_id=project.id,
                paper_id=paper.id,
                extracted=extracted,
                summary="; ".join(extracted.get("limitations", "") for _ in range(1)),
                token_cost=10,
            )
            self.db.add(analysis)
        self.db.commit()

        # WRITE
        self._update_stage(project, "WRITE", 90)
        evidence = [paper.abstract or paper.title for paper in project.papers]
        outline = f"Overview for {project.topic}"
        project.report_markdown = self.llm.write_markdown(outline, [e for e in evidence if e])
        self.db.commit()

        # EXPORT
        self._update_stage(project, "EXPORT", 95)
        self._create_exports(project)

        # DONE
        project.status = "completed"
        project.progress = 100
        project.stage = "DONE"
        self.db.commit()
        publish_project_event(project.id, "done", {"status": project.status})

    def _materialize_papers(self, project: Project, results: List):
        for meta in results:
            existing = (
                self.db.query(Paper)
                .filter(Paper.project_id == project.id, Paper.arxiv_id == meta.arxiv_id)
                .first()
            )
            if existing:
                continue
            paper = Paper(
                project_id=project.id,
                arxiv_id=meta.arxiv_id,
                title=meta.title,
                authors=meta.authors,
                abstract=meta.abstract,
                categories=meta.categories,
                published_at=meta.published_at,
                pdf_url=meta.pdf_url,
                download_status="ok",
            )
            self.db.add(paper)
        self.db.commit()
        self.db.refresh(project)

    def _create_exports(self, project: Project):
        storage_dir = project_storage_path(project.id)
        md_path = f"{storage_dir}/report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(project.report_markdown or "")
        export_md = Export(project_id=project.id, format="md", local_path=md_path, status="ok")
        self.db.add(export_md)
        self.db.commit()
