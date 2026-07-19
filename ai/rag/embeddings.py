from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Sequence


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class EmbeddingClient(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Return a float vector embedding for a single text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Return float vector embeddings for a list of texts."""
        pass


class MockEmbeddingClient(EmbeddingClient):
    """Deterministic pseudo-embedding generator using standard hashing for local testing."""

    def __init__(self, dimension: int = 64) -> None:
        self.dimension = dimension

    async def embed_text(self, text: str) -> list[float]:
        words = text.lower().split()
        vector = [0.0] * self.dimension
        if not words:
            return vector

        for word in words:
            # Deterministic hash mapping into dimensions
            h = hash(word)
            for d in range(self.dimension):
                val = math.sin(h * (d + 1))
                vector[d] += val

        # Normalize vector to unit length
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        results = []
        for t in texts:
            results.append(await self.embed_text(t))
        return results
