import os
from anthropic import AsyncAnthropic
from typing import List, Optional, Dict, Any
from .base import ModelProvider, ModelResponse, ModelInfo
import yaml

class AnthropicDirectProvider(ModelProvider):
    """Direct Anthropic API provider (fallback)"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
        self.models_config = self._load_models_config()
    
    def _load_models_config(self) -> Dict:
        """Load model configurations from YAML"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../config/models.yaml"
        )
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('models', {}).get('direct', {}).get('anthropic', {}).get('models', [])
    
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate text using Anthropic API"""
        if not self.client:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        max_tokens = max_tokens or 4096  # Anthropic requires max_tokens
        
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return ModelResponse(
            content=response.content[0].text,
            model=model,
            provider="anthropic",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
            metadata={
                "id": response.id,
            }
        )
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get available Anthropic models"""
        if not self.client:
            return []
        
        models = []
        for model_config in self.models_config:
            models.append(ModelInfo(
                id=model_config["name"],
                name=model_config["name"],
                display_name=model_config["display_name"],
                provider="anthropic",
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
        """Test Anthropic connection"""
        if not self.client:
            return False
        
        test_model = model or "claude-3-5-sonnet-20241022"
        try:
            response = await self.generate(
                prompt="Test",
                model=test_model,
                max_tokens=5
            )
            return True
        except Exception:
            return False

