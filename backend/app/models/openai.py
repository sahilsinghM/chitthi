import os
from openai import AsyncOpenAI
from typing import List, Optional, Dict, Any
from .base import ModelProvider, ModelResponse, ModelInfo
import yaml

class OpenAIDirectProvider(ModelProvider):
    """Direct OpenAI API provider (fallback)"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        self.models_config = self._load_models_config()
    
    def _load_models_config(self) -> Dict:
        """Load model configurations from YAML"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../config/models.yaml"
        )
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('models', {}).get('direct', {}).get('openai', {}).get('models', [])
    
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate text using OpenAI API"""
        if not self.client:
            raise ValueError("OPENAI_API_KEY not set")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        choice = response.choices[0]
        usage = response.usage
        
        return ModelResponse(
            content=choice.message.content,
            model=model,
            provider="openai",
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            finish_reason=choice.finish_reason,
            metadata={
                "id": response.id,
                "created": response.created,
            }
        )
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get available OpenAI models"""
        if not self.client:
            return []
        
        models = []
        for model_config in self.models_config:
            models.append(ModelInfo(
                id=model_config["name"],
                name=model_config["name"],
                display_name=model_config["display_name"],
                provider="openai",
                cost_per_1k_input=model_config.get("cost_per_1k_input", 0),
                cost_per_1k_output=model_config.get("cost_per_1k_output", 0),
            ))
        
        return models
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost based on model pricing"""
        model_config = next(
            (m for m in self.models_config if m["name"] == model),
            None
        )
        if not model_config:
            return 0.0
        
        input_cost = (input_tokens / 1000) * model_config.get("cost_per_1k_input", 0)
        output_cost = (output_tokens / 1000) * model_config.get("cost_per_1k_output", 0)
        return input_cost + output_cost
    
    async def test_connection(self, model: Optional[str] = None) -> bool:
        """Test OpenAI connection"""
        if not self.client:
            return False
        
        test_model = model or "gpt-3.5-turbo"
        try:
            response = await self.generate(
                prompt="Test",
                model=test_model,
                max_tokens=5
            )
            return True
        except Exception:
            return False

