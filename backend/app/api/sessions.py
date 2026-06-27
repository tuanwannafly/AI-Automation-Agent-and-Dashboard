from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
import json
from ..models.schemas import SessionState
from ..services.orchestrator import SessionManager

router = APIRouter()

# Specific routes must come before dynamic routes
@router.get("/export")
async def export_all_sessions(format: str = "json"):
    """Export all sessions - placeholder"""
    return JSONResponse(content={"success": True, "data": {"content": "", "filename": "all_sessions.json"}})

@router.get("/context")
async def get_all_sessions_context():
    """Get context for all sessions - placeholder"""
    return JSONResponse(content={"success": True, "data": {"sessions": []}})

@router.get("")
async def list_sessions():
    sessions = SessionManager.list_sessions()
    return JSONResponse(content={
        "success": True,
        "data": {"sessions": [s.model_dump() for s in sessions]}
    })

@router.get("/{session_id}")
async def get_session(session_id: str):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(content={
        "success": True,
        "data": session.model_dump()
    })

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    if not SessionManager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(content={"success": True})

@router.get("/{session_id}/export")
async def export_session(session_id: str, format: str = "markdown"):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if format == "json":
        content = json.dumps(session.model_dump(), indent=2)
        filename = f"session_{session_id}.json"
    else:
        lines = [f"# Session: {session_id}", ""]
        for msg in session.messages:
            role = msg.role.capitalize()
            lines.append(f"## {role}\n\n{msg.content}\n")
        
        if session.reasoning_chain:
            lines.append("\n## Reasoning Chain\n")
            for i, step in enumerate(session.reasoning_chain, 1):
                lines.append(f"{i}. **{step.type}**: {step.content}")
        
        content = "\n".join(lines)
        filename = f"session_{session_id}.md"
    
    return JSONResponse(content={
        "success": True,
        "data": {"content": content, "filename": filename}
    })

@router.post("/{session_id}/memory")
async def save_session_memory(session_id: str):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(content={"success": True})

@router.get("/{session_id}/context")
async def get_session_context(session_id: str):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context = {
        "sessionId": session.id,
        "messagesCount": len(session.messages),
        "reasoningStepsCount": len(session.reasoning_chain),
        "provider": session.current_provider
    }
    
    return JSONResponse(content={"success": True, "data": context})