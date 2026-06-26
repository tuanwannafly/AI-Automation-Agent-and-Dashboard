from pydantic import BaseModel
from typing import Optional, List, Literal


class ChatRequest(BaseModel):
    message: str
    file_ids: Optional[List[str]] = None
    llm_provider: Optional[Literal["groq", "openai", "gemini"]] = "groq"


class ChatResponse(BaseModel):
    session_id: str
    ws_url: str
    status: str = "running"


class SessionState(BaseModel):
    session_id: str
    messages: List[dict] = []
    reasoning_chain: List[dict] = []
    created_at: Optional[str] = None