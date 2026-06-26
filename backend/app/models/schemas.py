from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum
from datetime import datetime

class AgentEventType(str, Enum):
    THINKING = "THINKING"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    STREAMING_TOKEN = "STREAMING_TOKEN"
    WORKFLOW_STEP = "WORKFLOW_STEP"
    DONE = "DONE"
    ERROR = "ERROR"
    PONG = "PONG"

class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    GEMINI = "gemini"

class Message(BaseModel):
    id: str
    role: str
    content: str
    timestamp: float
    reasoning: Optional[list] = None
    tool_calls: Optional[list] = None
    tool_results: Optional[list] = None

class ReasoningStep(BaseModel):
    id: str
    type: str
    content: str
    data: Optional[Any] = None
    timestamp: float

class SessionState(BaseModel):
    id: str
    messages: list[Message] = []
    reasoning_chain: list[ReasoningStep] = []
    is_running: bool = False
    is_streaming: bool = False
    error: Optional[str] = None
    current_provider: LLMProvider = LLMProvider.GROQ
    created_at: float = datetime.now().timestamp()
    updated_at: float = datetime.now().timestamp()

class AgentEvent(BaseModel):
    type: AgentEventType
    data: Any
    timestamp: float = datetime.now().timestamp()
    id: str = ""

class CreateChatRequest(BaseModel):
    message: str
    llm_provider: Optional[LLMProvider] = None
    session_context: Optional[dict] = None

class CreateChatResponse(BaseModel):
    sessionId: str
    message: Message

class ChatMessage(BaseModel):
    message: str
    llm_provider: Optional[LLMProvider] = None