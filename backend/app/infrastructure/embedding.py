from typing import List
import random
from typing import List


class EmbeddingProvider:
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return dense vectors for a batch of texts."""

        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts: List[str]) -> List[List[float]]:
        # Deterministic-ish mock vectors so tests are stable but non-zero.
        random.seed(0)
        return [[random.random() for _ in range(8)] for _ in texts]
