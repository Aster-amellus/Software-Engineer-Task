import time
from dataclasses import dataclass
from datetime import datetime
from typing import List
import httpx
import xml.etree.ElementTree as ET

from core.config import get_settings


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
    def search(self, query: str, start: int, max_results: int, sort_by: str = "submittedDate", sort_order: str = "descending") -> List[PaperMetadata]:
        """Query the arXiv Atom feed. Defaults are safe for MVP; callers may inject small max_results."""

        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        url = "https://export.arxiv.org/api/query"
        resp = httpx.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return self.parse_feed(resp.text)

    @staticmethod
    def parse_feed(atom_xml: str) -> List[PaperMetadata]:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(atom_xml)
        papers: list[PaperMetadata] = []
        for entry in root.findall("atom:entry", ns):
            arxiv_id = entry.findtext("atom:id", default="", namespaces=ns).split("/")[-1]
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            abstract = entry.findtext("atom:summary", default="", namespaces=ns).strip()
            authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
            categories = [c.attrib.get("term", "") for c in entry.findall("atom:category", ns)]
            published_raw = entry.findtext("atom:published", default="", namespaces=ns)
            published_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00")) if published_raw else datetime.utcnow()
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("type") == "application/pdf":
                    pdf_url = link.attrib.get("href", "")
                    break
            papers.append(
                PaperMetadata(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    categories=categories,
                    published_at=published_at,
                    pdf_url=pdf_url,
                )
            )
        return papers


class MockArxivAdapter(ArxivAdapter):
    def search(self, query: str, start: int, max_results: int, sort_by: str = "submittedDate", sort_order: str = "descending") -> List[PaperMetadata]:
        # Sleep lightly to mimic the recommended polite delay without slowing tests too much.
        time.sleep(0.05)
        return [
            PaperMetadata(
                arxiv_id=f"{query}-mvp-{i}",
                title=f"{query} paper {i}",
                authors=["Jane Doe", "John Doe"],
                abstract=f"A mock abstract for {query} with index {i}.",
                categories=["cs.AI"],
                published_at=datetime.utcnow(),
                pdf_url=f"http://example.com/{query}-{i}.pdf",
            )
            for i in range(start, start + max_results)
        ]
