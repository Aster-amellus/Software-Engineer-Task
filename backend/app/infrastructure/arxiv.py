from dataclasses import dataclass
from typing import List
from datetime import datetime

from models import Paper


@dataclass
class PaperMetadata:
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published_at: datetime
    pdf_url: str


class ArxivAdapter:
    def search(self, query: str, start: int, max_results: int) -> List[PaperMetadata]:
        # Mock implementation for MVP
        return [
            PaperMetadata(
                arxiv_id="1234.5678",
                title="Mock Paper on {query}",
                authors=["John Doe"],
                abstract="This is a mock abstract about " + query,
                categories=["cs.AI"],
                published_at=datetime.utcnow(),
                pdf_url="http://example.com/mock.pdf",
            ),
            PaperMetadata(
                arxiv_id="2345.6789",
                title="Another Mock Paper",
                authors=["Jane Doe"],
                abstract="Additional mock abstract about " + query,
                categories=["cs.CL"],
                published_at=datetime.utcnow(),
                pdf_url="http://example.com/mock2.pdf",
            ),
        ][:max_results]


class MockArxivAdapter(ArxivAdapter):
    pass
