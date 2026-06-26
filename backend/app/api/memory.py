from fastapi import APIRouter, HTTPException
from app.services.session import SessionManager
from app.services.memory import AgentMemory
import json

router = APIRouter()
memory = AgentMemory()


@router.get("/sessions/{session_id}/export")
async def export_session(session_id: str, format: str = "markdown"):
    """Export session as Markdown or JSON."""
    state = await SessionManager.get_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    if format == "json":
        return state

    # Markdown format
    md = f"# AI Agent Session: {session_id}\n\n"
    md += f"**Query:** {state.get('user_query', 'N/A')}\n\n"
    md += f"**Final Answer:**\n{state.get('final_answer', 'N/A')}\n\n"

    if state.get('reasoning_chain'):
        md += "## Reasoning Chain\n\n"
        for i, step in enumerate(state['reasoning_chain'], 1):
            md += f"### Step {i}: {step.get('type', 'Unknown')}\n"
            md += f"{step.get('content', step.get('result_preview', 'N/A'))}\n\n"

    if state.get('tool_calls'):
        md += "## Tool Calls\n\n"
        for call in state['tool_calls']:
            md += f"- **{call.get('tool', 'unknown')}**: {call.get('output', 'N/A')[:200]}\n"

    return {"content": md, "format": "markdown"}


@router.post("/sessions/{session_id}/memory")
async def save_session_memory(session_id: str, data: dict):
    """Save session summary to memory for future context."""
    query = data.get("query", "")
    answer = data.get("answer", "")
    await memory.save_turn(session_id, query, answer)
    return {"saved": True}


@router.get("/sessions/{session_id}/context")
async def get_session_context(session_id: str):
    """Get context from previous sessions."""
    context = await memory.load_context(session_id)
    return {"context": context or "No previous context available"}