import os
from typing import List, Dict, Optional
from phidata.agent import Agent
from phidata.models.openrouter import OpenRouter

class TopicAgent:
    """Agno agent for topic clustering and prioritization"""
    
    def __init__(self, model_id: str = "openai/gpt-4-turbo"):
        self.model_id = model_id
        
        self.model = OpenRouter(
            model=model_id,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        self.agent = Agent(
            name="TopicAgent",
            role="Cluster content into topics and prioritize newsletter themes",
            model=self.model,
            instructions="""You are a topic clustering and prioritization agent. Your job is to:
1. Analyze multiple content items
2. Cluster them into related themes (e.g., "AI x Design", "Startup Economics")
3. Rank topics based on:
   - Interest weight (from user tags)
   - Recency/trend signals
   - Potential for engaging newsletter content
4. Output 3-5 shortlisted topics for the week
5. Provide reasoning for each ranking""",
            markdown=True,
            structured_outputs=True,
        )
    
    async def prioritize_topics(
        self,
        content_items: List[Dict],
        interest_weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict]:
        """Prioritize topics from content items"""
        # Format content for agent
        content_summary = "\n\n".join([
            f"Item {i+1}: {item.get('summary', item.get('title', 'No title'))}\n"
            f"Tags: {', '.join(item.get('tags', []))}"
            for i, item in enumerate(content_items)
        ])
        
        prompt = f"""Analyze these content items and create prioritized topics for newsletter:

{content_summary}

{f'Interest weights: {interest_weights}' if interest_weights else ''}

Output 3-5 prioritized topics with:
- Topic title
- Description
- Priority score (1-10)
- Related content items
- Reasoning for ranking"""
        
        response = await self.agent.arun(prompt)
        
        # Parse structured output (Agno will handle this)
        # For now, return raw response - will be enhanced with structured output parsing
        return [{
            "title": "Topic",
            "description": response.content if hasattr(response, 'content') else str(response),
            "priority_score": 7.5,
            "items": content_items,
        }]

