from typing import TypedDict, List, Optional, Literal
from pydantic import BaseModel


class AgentState(TypedDict, total=False):
    # Input
    user_query: str
    uploaded_files: List[str]
    workflow_config: Optional[dict]

    # Runtime
    plan: List[str]
    tool_calls: List[dict]
    tool_results: List[dict]
    current_step: int
    max_iterations: int

    # Output
    final_answer: str
    reasoning_chain: List[dict]

    # Meta
    session_id: str
    llm_provider: Literal["groq", "openai", "gemini"]
    tokens_used: int
    execution_time_ms: int
    error: Optional[str]