from typing import List


class LLMProvider:
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        raise NotImplementedError

    def write_markdown(self, outline: str, evidence: List[str]) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        return {
            "methodology": {"name": "mock", "steps": ["step1", "step2"]},
            "datasets": [{"name": "mock-dataset", "desc": "synthetic"}],
            "metrics": [{"name": "acc", "value": "0.9", "setting": "mock"}],
            "limitations": "mock limitations",
        }

    def write_markdown(self, outline: str, evidence: List[str]) -> str:
        return f"# Summary\n\n{outline}\n\n" + "\n".join(evidence)
