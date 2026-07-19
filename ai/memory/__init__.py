"""Memory System package.

Provides abstract boundaries and in-memory mock adapters for fact retrieval and storage.
"""

from .service import InMemoryMemoryAdapter
from .models import MemoryRecord
from .compressor import MemoryCompressor

__all__ = ["InMemoryMemoryAdapter", "MemoryRecord", "MemoryCompressor"]
