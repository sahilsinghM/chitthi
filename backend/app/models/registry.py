import os
from typing import List, Optional, Dict
from .base import ModelProvider, ModelResponse, ModelInfo
from .openrouter import OpenRouterProvider
from .openai import OpenAIDirectProvider
from .anthropic import AnthropicDirectProvider
import yaml

class ModelRegistry:
    """Central registry for managing all model providers"""
    
    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.config = self._load_config()
        self._initialize_providers()
    
    def _load_config(self) -> Dict:
        """Load model configuration"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../config/models.yaml"
        )
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_providers(self):
        """Initialize enabled providers"""
        # OpenRouter (primary)
        if self.config.get('models', {}).get('openrouter', {}).get('enabled', False):
            if os.getenv("OPENROUTER_API_KEY"):
                self.providers["openrouter"] = OpenRouterProvider()
        
        # Direct OpenAI (fallback)
        if self.config.get('models', {}).get('direct', {}).get('openai', {}).get('enabled', False):
            if os.getenv("OPENAI_API_KEY"):
                self.providers["openai"] = OpenAIDirectProvider()
        
        # Direct Anthropic (fallback)
        if self.config.get('models', {}).get('direct', {}).get('anthropic', {}).get('enabled', False):
            if os.getenv("ANTHROPIC_API_KEY"):
                self.providers["anthropic"] = AnthropicDirectProvider()
    
    async def get_all_models(self) -> List[ModelInfo]:
        """Get all available models from all providers"""
        all_models = []
        for provider in self.providers.values():
            try:
                models = await provider.get_available_models()
                all_models.extend(models)
            except Exception as e:
                print(f"Error fetching models from provider: {e}")
        return all_models
    
    async def generate(
        self,
        prompt: str,
        model_id: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> ModelResponse:
        """
        Generate text using specified model with automatic fallback.
        
        Args:
            model_id: Full model ID (e.g., "openai/gpt-4-turbo" or "gpt-4-turbo")
            use_fallback: If True, try direct API if OpenRouter fails
        """
        # Determine provider from model_id
        provider_name = self._get_provider_from_model(model_id)
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not available for model: {model_id}")
        
        provider = self.providers[provider_name]
        
        try:
            return await provider.generate(
                prompt=prompt,
                model=model_id,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            # Fallback logic: if OpenRouter fails, try direct API
            if use_fallback and provider_name == "openrouter":
                # Extract base model name (e.g., "gpt-4-turbo" from "openai/gpt-4-turbo")
                base_model = model_id.split("/")[-1] if "/" in model_id else model_id
                
                # Try OpenAI direct
                if "openai" in model_id.lower() and "openai" in self.providers:
                    try:
                        return await self.providers["openai"].generate(
                            prompt=prompt,
                            model=base_model,
                            system_prompt=system_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            **kwargs
                        )
                    except Exception:
                        pass
                
                # Try Anthropic direct
                if "claude" in model_id.lower() and "anthropic" in self.providers:
                    try:
                        return await self.providers["anthropic"].generate(
                            prompt=prompt,
                            model=base_model,
                            system_prompt=system_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            **kwargs
                        )
                    except Exception:
                        pass
            
            raise e
    
    def _get_provider_from_model(self, model_id: str) -> Optional[str]:
        """Determine provider from model ID"""
        if model_id.startswith("openai/"):
            # OpenRouter OpenAI model
            return "openrouter"
        elif model_id.startswith("anthropic/"):
            # OpenRouter Anthropic model
            return "openrouter"
        elif model_id.startswith("meta-llama/"):
            # OpenRouter Llama model
            return "openrouter"
        elif any(m in model_id.lower() for m in ["gpt-3", "gpt-4"]):
            # OpenAI model
            return "openai" if "openai" in self.providers else "openrouter"
        elif "claude" in model_id.lower():
            # Anthropic model
            return "anthropic" if "anthropic" in self.providers else "openrouter"
        else:
            # Default to openrouter if available
            return "openrouter" if "openrouter" in self.providers else None
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """Estimate cost for token usage"""
        provider_name = self._get_provider_from_model(model_id)
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name].estimate_cost(
                input_tokens, output_tokens, model_id
            )
        return 0.0
    
    async def test_provider(self, provider_name: str) -> bool:
        """Test if a provider is accessible"""
        if provider_name not in self.providers:
            return False
        return await self.providers[provider_name].test_connection()

