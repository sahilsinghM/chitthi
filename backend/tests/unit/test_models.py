import pytest
from unittest.mock import AsyncMock, patch
from app.models.base import ModelResponse, ModelInfo

@pytest.mark.unit
class TestModelResponse:
    def test_model_response_creation(self):
        response = ModelResponse(
            content="Test response",
            model="gpt-4",
            provider="openai",
            input_tokens=10,
            output_tokens=20
        )
        assert response.content == "Test response"
        assert response.input_tokens == 10
        assert response.output_tokens == 20

@pytest.mark.unit
class TestModelInfo:
    def test_model_info_creation(self):
        info = ModelInfo(
            id="gpt-4",
            name="gpt-4",
            display_name="GPT-4",
            provider="openai",
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06
        )
        assert info.id == "gpt-4"
        assert info.provider == "openai"

