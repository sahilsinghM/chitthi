import os
from typing import Optional
from phidata.agent import Agent
from phidata.models.openai import OpenAIChat
from phidata.models.anthropic import Claude
from phidata.models.openrouter import OpenRouter

from app.models.registry import ModelRegistry

class DraftAgent:
    """Agno agent for generating newsletter drafts"""
    
    def __init__(self, model_id: str, registry: ModelRegistry):
        self.model_id = model_id
        self.registry = registry
        
        # Determine model type and create appropriate Agno model
        self.agno_model = self._create_agno_model(model_id)
        
        # Create Agno agent with newsletter-specific instructions
        self.agent = Agent(
            name="NewsletterDraftAgent",
            role="Generate Hinglish newsletter drafts",
            model=self.agno_model,
            instructions=self._get_instructions(),
            markdown=True,
            structured_outputs=True,
        )
    
    def _create_agno_model(self, model_id: str):
        """Create Agno model instance based on model_id"""
        if model_id.startswith("openai/"):
            # OpenRouter OpenAI model
            return OpenRouter(
                model=model_id,
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
        elif model_id.startswith("anthropic/"):
            # OpenRouter Anthropic model
            return OpenRouter(
                model=model_id,
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
        elif model_id.startswith("meta-llama/"):
            # OpenRouter Llama model
            return OpenRouter(
                model=model_id,
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
        elif any(m in model_id.lower() for m in ["gpt-3", "gpt-4"]):
            # Direct OpenAI
            return OpenAIChat(
                model=model_id,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif "claude" in model_id.lower():
            # Direct Anthropic
            return Claude(
                model=model_id,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        else:
            # Default to OpenRouter
            return OpenRouter(
                model=model_id,
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
    
    def _get_instructions(self) -> str:
        """Get agent instructions for Hinglish newsletter generation"""
        return """You are a newsletter writer creating content in Hinglish (English script with Hindi words mixed naturally).

Style Guidelines:
- English for logic and technical concepts
- Hindi for emotion and cultural context
- Sharp, witty, builder-energy tone
- Target audience: Engineers, designers, founders, builders
- Length: 500-800 words

Structure Required:
1. Hook - Insightful or witty observation
2. Context - Explain the topic simply
3. Insight - Core argument or framework
4. Takeaway - What reader learns / feels
5. Closing - Punchline or curiosity loop

References: Naval, Paul Graham, Sahil Bloom, Raj Shamani, Varun Mayya
Write naturally, mixing English and Hindi words seamlessly."""
    
    async def generate(
        self,
        context: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2000,
    ) -> dict:
        """Generate newsletter draft using Agno agent"""
        prompt = f"""Generate a Hinglish newsletter based on this context:

{context}

Follow the structure and style guidelines provided. Make it engaging, informative, and naturally mixing English and Hindi."""
        
        response = await self.agent.arun(prompt, temperature=temperature, max_tokens=max_tokens)
        
        return {
            "content": response.content if hasattr(response, 'content') else str(response),
            "model": self.model_id,
            "agent": "DraftAgent",
        }



