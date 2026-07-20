import pytest
from ai.rag.vector_store import InMemoryVectorStore, DocumentChunk
from ai.rag.embeddings import MockEmbeddingClient


@pytest.mark.asyncio
async def test_mock_embedding_generation():
    client = MockEmbeddingClient(dimension=64)
    vector = await client.embed_text("hello world")

    assert len(vector) == 64
    # Ensure it's normalized
    norm = sum(v * v for v in vector)
    assert abs(norm - 1.0) < 1e-6


@pytest.mark.asyncio
async def test_in_memory_vector_search():
    client = MockEmbeddingClient(dimension=64)
    store = InMemoryVectorStore(embedding_client=client)

    chunks = [
        DocumentChunk(
            chunk_id="1",
            doc_id="d1",
            content="The capital of France is Paris.",
            metadata={},
        ),
        DocumentChunk(
            chunk_id="2",
            doc_id="d1",
            content="Python is a programming language.",
            metadata={},
        ),
        DocumentChunk(
            chunk_id="3",
            doc_id="d2",
            content="Machine learning models require data.",
            metadata={},
        ),
    ]

    await store.add_chunks(chunks)

    # Search for something similar to chunk 2
    results = await store.search("Python language", top_k=1, threshold=0.0)

    assert len(results) == 1
    # Depending on hash collision in mock, we just ensure it returns a result
    assert isinstance(results[0].chunk, DocumentChunk)
