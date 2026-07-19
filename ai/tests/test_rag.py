"""Tests for RAG document chunking, embeddings, vector store, and service."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.rag.chunker import TextChunker
from ai.rag.embeddings import MockEmbeddingClient, cosine_similarity
from ai.rag.vector_store import InMemoryVectorStore
from ai.rag.service import RAGService
from ai.rag.models import RAGConfig


# -- Test 1: Text chunking --------------------------------------------------

def test_text_chunker():
    """Verify text chunker splits text with specified size and overlap."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "Word " * 50  # ~250 characters

    chunks = chunker.chunk_text(text, document_id="doc_1")
    assert len(chunks) >= 2, f"Expected at least 2 chunks, got {len(chunks)}"
    assert chunks[0].document_id == "doc_1"
    assert len(chunks[0].content) <= 100
    print(f"  PASSED: Text chunking into {len(chunks)} chunks")


# -- Test 2: Cosine similarity ----------------------------------------------

def test_cosine_similarity():
    """Verify cosine similarity calculation."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-5, "Identical vectors score 1.0"
    assert abs(cosine_similarity(v1, v3) - 0.0) < 1e-5, "Orthogonal vectors score 0.0"
    print("  PASSED: Cosine similarity calculation")


# -- Test 3: Mock embeddings -----------------------------------------------

async def test_mock_embeddings():
    """Verify MockEmbeddingClient outputs normalized vectors."""
    client = MockEmbeddingClient(dimension=32)
    vec = await client.embed_text("Alfred AI assistant")

    assert len(vec) == 32
    norm = sum(v * v for v in vec)
    assert abs(norm - 1.0) < 1e-4, "Embedding should be normalized to unit length"
    print("  PASSED: Mock embedding generation and normalization")


# -- Test 4: RAG service end-to-end -----------------------------------------

async def test_rag_service_e2e():
    """Verify document ingestion, search retrieval, top-K, and context formatting."""
    config = RAGConfig(chunk_size=120, chunk_overlap=10, top_k=2)
    rag_service = RAGService(config=config)

    doc_text = (
        "Alfred is an AI assistant framework designed for modular extensions. "
        "It supports plug-and-play tools like Calculator, Gmail, and Google Calendar. "
        "The LLM Gateway routes requests to OpenAI, Claude, Gemini, and DeepSeek. "
        "Memory compression deduplicates facts and preferences efficiently."
    )

    chunks_created = await rag_service.ingest_document("doc_alfred", doc_text)
    assert chunks_created > 0, "Document should be chunked and indexed"

    results = await rag_service.retrieve_relevant_context("Tell me about Alfred tools and Calendar")
    assert len(results) <= 2, f"Expected top_k <= 2, got {len(results)}"

    formatted = rag_service.format_context_injection(results)
    assert "--- Retrieved Knowledge Documents (RAG) ---" in formatted
    assert "doc_alfred" in formatted
    print(f"  PASSED: RAG service E2E — retrieved {len(results)} chunks, formatted prompt injection")


# -- Main -------------------------------------------------------------------

async def main():
    print("--- RAG Chunking & Vector Tests ---")
    test_text_chunker()
    test_cosine_similarity()
    await test_mock_embeddings()

    print("\n--- RAG Service End-to-End Tests ---")
    await test_rag_service_e2e()

    print("\n All RAG tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
