from pydantic import BaseModel
from typing import Optional, List, Literal, Any
from pydantic import field_validator


class WorkflowInput(BaseModel):
    name: str
    type: Literal["file", "text", "number", "boolean"]
    accept: Optional[List[str]] = None
    required: bool = True
    default: Any = None


class WorkflowStep(BaseModel):
    id: str
    tool: Literal["code_executor", "llm_call", "rag_search", "web_search", "summarizer"]
    description: Optional[str] = None
    condition: Optional[str] = None
    code: Optional[str] = None
    prompt: Optional[str] = None
    provider: Optional[str] = "groq"
    query: Optional[str] = None
    collection: Optional[str] = "documents"
    top_k: Optional[int] = 5
    input: Optional[dict] = None
    output_as: str

    @field_validator('code')
    @classmethod
    def code_required_for_code_executor(cls, v, info):
        if info.data.get('tool') == 'code_executor' and not v:
            raise ValueError("code is required for code_executor tool")
        return v


class WorkflowConfig(BaseModel):
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    inputs: List[WorkflowInput] = []
    steps: List[WorkflowStep]
    outputs: List[str]