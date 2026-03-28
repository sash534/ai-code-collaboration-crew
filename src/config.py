import os
import litellm
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

litellm.set_verbose = False


def get_llm():
    """Return LLM based on available environment"""

    if os.getenv("OPENAI_API_KEY"):
        return LLM(
            model="gpt-4o-mini",
            temperature=0.2
        )
    elif os.getenv("GROQ_API_KEY"):
        return LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
            max_retries=5,
        )
    else:
        return LLM(
            model="ollama/llama3:8b",
            base_url="http://localhost:11434",
            temperature=0.2
        )