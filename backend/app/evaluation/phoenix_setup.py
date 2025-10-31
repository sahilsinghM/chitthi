"""Phoenix tracing setup for newsletter engine"""
import os
from typing import Optional

# Phoenix setup is optional - only enable if PHOENIX_HOST is set
PHOENIX_HOST = os.getenv("PHOENIX_HOST")
PHOENIX_ENABLED = PHOENIX_HOST is not None

def setup_phoenix_tracing():
    """Set up Phoenix tracing for LLM calls"""
    if not PHOENIX_ENABLED:
        return None
    
    try:
        from phoenix.trace.openai import OpenAIInstrumentor
        from phoenix.trace.langchain import LangChainInstrumentor
        from openai import OpenAI, AsyncOpenAI
        from langchain_openai import ChatOpenAI
        
        # Instrument OpenAI clients
        OpenAIInstrumentor().instrument()
        
        # Instrument LangChain if used
        try:
            LangChainInstrumentor().instrument()
        except Exception:
            pass  # LangChain might not be used
        
        print(f"Phoenix tracing enabled: {PHOENIX_HOST}")
        return True
    except ImportError:
        print("Phoenix not installed. Install with: pip install arize-phoenix")
        return None
    except Exception as e:
        print(f"Failed to setup Phoenix tracing: {e}")
        return None

# Auto-setup on import if enabled
if PHOENIX_ENABLED:
    setup_phoenix_tracing()

