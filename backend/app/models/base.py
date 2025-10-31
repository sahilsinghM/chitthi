from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from dataclasses import dataclass

class ModelResponse(BaseModel):
    """Standardized response from any model provider"""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ModelInfo(BaseModel):
    """Information about an available model"""
    id: str
    name: str
    display_name: str
    provider: str  # 'openrouter', 'openai', 'anthropic'
    cost_per_1k_input: float
    cost_per_1k_output: float
    available: bool = True
    description: Optional[str] = None

class ModelProvider(ABC):
    """Base interface for all model providers"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate text using the specified model"""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from this provider"""
        pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for token usage"""
        pass
    
    @abstractmethod
    async def test_connection(self, model: Optional[str] = None) -> bool:
        """Test if provider is accessible"""
        pass

