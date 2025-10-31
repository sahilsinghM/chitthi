import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from app.models.registry import ModelRegistry

# Set test environment variables
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

@pytest.fixture
def mock_registry():
    """Mock model registry for testing"""
    registry = MagicMock(spec=ModelRegistry)
    return registry

@pytest.fixture
async def test_registry():
    """Real registry instance for integration tests (requires API keys)"""
    return ModelRegistry()

