import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Automation Agent"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    DEFAULT_LLM_PROVIDER: str = "groq"
    DEFAULT_MODEL_GROQ: str = "llama-3.1-70b-versatile"
    DEFAULT_MODEL_OPENAI: str = "gpt-4o-mini"
    DEFAULT_MODEL_GEMINI: str = "gemini-1.5-flash"
    
    MAX_ITERATIONS: int = 10
    TIMEOUT_SECONDS: int = 120
    
    WORKFLOWS_DIR: str = os.path.join(os.path.dirname(__file__), "..", "workflows")
    UPLOADS_DIR: str = os.path.join(os.path.dirname(__file__), "..", "uploads")
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

settings = Settings()