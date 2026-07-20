import pytest
from uuid import uuid4
import uuid
from unittest.mock import patch, MagicMock

from app.database.models.memory import Memory
from app.services.memory_service import MemoryService
from app.repositories.memory_repository import MemoryRepository
from app.services import EventDispatcher


@pytest.mark.asyncio
async def test_memory_encryption(test_user_id: uuid.UUID):
    # Mock repository and event dispatcher
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_events = MagicMock(spec=EventDispatcher)

    # Set up mock to return a Memory object
    mock_memory = Memory(
        id=uuid4(), user_id=test_user_id, content="encrypted_text", category="test"
    )
    mock_repo.create.return_value = mock_memory

    service = MemoryService(memories=mock_repo, events=mock_events)

    # Mock embedding to avoid external API calls
    with patch.object(service, "_get_embedding", return_value=[0.1] * 1536):
        memory = await service.store_memory(
            test_user_id, "my secret password", category="secret"
        )

    # Ensure memory was created and content returned is plaintext
    assert memory.content == "my secret password"
    # Ensure what was passed to repo is encrypted
    args, _ = mock_repo.create.call_args
    assert args[1] != "my secret password"


@pytest.mark.asyncio
async def test_memory_search(test_user_id: uuid.UUID):
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_events = MagicMock(spec=EventDispatcher)

    # Mock search result returning a single memory with encrypted content
    service = MemoryService(memories=mock_repo, events=mock_events)
    encrypted_content = service._encrypt("test memory")
    mock_repo.search_by_vector.return_value = [
        Memory(id=uuid4(), user_id=test_user_id, content=encrypted_content)
    ]

    with patch.object(service, "_get_embedding", return_value=[0.1] * 1536):
        results = await service.search_memories(test_user_id, "query")

    assert len(results) == 1
    # Verify decryption happened correctly
    assert results[0].content == "test memory"
