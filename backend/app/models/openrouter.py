import os
import httpx
from typing import List, Optional, Dict, Any
from .base import ModelProvider, ModelResponse, ModelInfo
import yaml

class OpenRouterProvider(ModelProvider):
    """OpenRouter API provider - unified access to 100+ models"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.models_config = self._load_models_config()
    
    def _load_models_config(self) -> Dict:
        """Load model configurations from YAML"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../config/models.yaml"
        )
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('models', {}).get('openrouter', {}).get('models', [])
    
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate text using OpenRouter API"""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/yourusername/chitthi",
            "X-Title": "Newsletter Engine",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        
        choice = data["choices"][0]
        usage = data.get("usage", {})
        
        return ModelResponse(
            content=choice["message"]["content"],
            model=model,
            provider="openrouter",
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason"),
            metadata={
                "id": data.get("id"),
                "created": data.get("created"),
            }
        )
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get available models from OpenRouter"""
        if not self.api_key:
            return []
        
        # Get models from config first
        models = []
        for model_config in self.models_config:
            models.append(ModelInfo(
                id=model_config["name"],
                name=model_config["name"],
                display_name=model_config["display_name"],
                provider="openrouter",
                cost_per_1k_input=model_config.get("cost_per_1k_input", 0),
                cost_per_1k_output=model_config.get("cost_per_1k_output", 0),
                description=model_config.get("description")
            ))
        
        # Optionally fetch live model list from OpenRouter API
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    # Merge with config models, update availability
                    live_models = {m["id"]: m for m in data.get("data", [])}
                    for model in models:
                        if model.id in live_models:
                            model.available = True
        except Exception:
            # If API fails, use config models
            pass
        
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
        """Test OpenRouter connection"""
        if not self.api_key:
            return False
        
        test_model = model or "openai/gpt-3.5-turbo"  # Cheapest test model
        try:
            response = await self.generate(
                prompt="Test",
                model=test_model,
                max_tokens=5
            )
            return True
        except Exception:
            return False

