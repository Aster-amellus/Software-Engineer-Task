from typing import List
import random


class EmbeddingProvider:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[random.random() for _ in range(4)] for _ in texts]
