import os
from typing import List, Optional
from phidata.agent import Agent
from phidata.models.openrouter import OpenRouter
from phidata.tools.website import WebsiteReader

class ContentAgent:
    """Agno agent for content ingestion and processing"""
    
    def __init__(self, model_id: str = "openai/gpt-4-turbo"):
        self.model_id = model_id
        
        # Create OpenRouter model for content processing
        self.model = OpenRouter(
            model=model_id,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        # Create agent with website reading tools
        self.agent = Agent(
            name="ContentAgent",
            role="Extract and summarize content from URLs",
            model=self.model,
            instructions="""You are a content extraction agent. Your job is to:
1. Read and understand content from URLs
2. Extract key insights and information
3. Summarize content in a structured format
4. Identify relevant tags and topics
5. Ask clarifying questions if needed""",
            tools=[WebsiteReader()],
            markdown=True,
        )
    
    async def ingest_url(self, url: str, notes: Optional[str] = None) -> dict:
        """Ingest content from URL"""
        prompt = f"Extract and summarize the key insights from this URL: {url}"
        if notes:
            prompt += f"\n\nUser notes: {notes}"
        
        response = await self.agent.arun(prompt)
        
        return {
            "url": url,
            "summary": response.content if hasattr(response, 'content') else str(response),
            "extracted_at": "now",  # TODO: Add proper timestamp
        }
    
    async def ask_clarifying_questions(self, url: str) -> List[str]:
        """Ask AI to generate clarifying questions about the content"""
        prompt = f"""Based on this URL: {url}
Generate 2-3 clarifying questions in Hinglish to help extract the most relevant information.
Questions should be like:
- "Tumhe is article se kya extract karna hai?"
- "Kis lens se dekhna hai — builder, economy, ya design?""""
        
        response = await self.agent.arun(prompt)
        # Parse questions from response
        content = response.content if hasattr(response, 'content') else str(response)
        questions = [q.strip() for q in content.split('\n') if q.strip() and '?' in q]
        return questions[:3]  # Return max 3 questions

