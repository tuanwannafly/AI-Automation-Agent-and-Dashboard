from pydantic import BaseModel
from typing import Literal, Optional, Any


class AgentEvent(BaseModel):
    type: Literal[
        "THINKING", "TOOL_CALL", "TOOL_RESULT",
        "CODE_EXECUTING", "CODE_RESULT",
        "STREAMING_TOKEN", "WORKFLOW_STEP",
        "DONE", "ERROR", "PONG"
    ]
    content: Optional[str] = None
    step: Optional[int] = None
    tool: Optional[str] = None
    input: Optional[dict] = None
    output: Optional[str] = None
    duration_ms: Optional[int] = None
    token: Optional[str] = None
    step_id: Optional[str] = None
    description: Optional[str] = None
    final_answer: Optional[str] = None
    reasoning_chain: Optional[list] = None
    total_tokens: Optional[int] = None
    total_time_ms: Optional[int] = None
    outputs: Optional[dict] = None
    message: Optional[str] = None
    recoverable: Optional[bool] = None