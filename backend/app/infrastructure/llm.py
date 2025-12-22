import httpx
from typing import List

from core.config import get_settings


class LLMProvider:
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        raise NotImplementedError

    def write_markdown(self, outline: str, evidence: List[str]) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        return {
            "methodology": {"name": "mock", "steps": ["stage", "result"]},
            "datasets": [{"name": "mock-dataset", "desc": "synthetic"}],
            "metrics": [{"name": "acc", "value": "0.9", "setting": "mock"}],
            "limitations": "mock limitations",
        }

    def write_markdown(self, outline: str, evidence: List[str]) -> str:
        body = "\n\n".join(f"- {ev}" for ev in evidence if ev)
        return f"# Summary\n\n{outline}\n\n## Evidence\n{body}\n"


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _post(self, path: str, payload: dict) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.base_url}/{path.lstrip('/') }"
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def generate_structured(self, prompt: str, schema: dict) -> dict:
        data = self._post(
            "v1/chat/completions",
            {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_schema", "json_schema": schema or {}},
            },
        )
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        try:
            return httpx.Response(200, text=content).json()
        except Exception:
            return {}

    def write_markdown(self, outline: str, evidence: List[str]) -> str:
        joined = "\n".join(evidence)
        data = self._post(
            "v1/chat/completions",
            {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Write a concise markdown literature review."},
                    {"role": "user", "content": f"Outline:{outline}\nEvidence:{joined}"},
                ],
            },
        )
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


def resolve_llm_provider(name: str | None = None) -> LLMProvider:
    settings = get_settings()
    name = (name or settings.llm_provider).lower()
    if name == "openai_compat" and settings.openai_base_url and settings.openai_api_key:
        return OpenAICompatibleProvider(settings.openai_base_url, settings.openai_api_key)
    return MockLLMProvider()
