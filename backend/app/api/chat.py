from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
from ..models.schemas import (
    CreateChatRequest, CreateChatResponse, Message,
    ChatMessage, LLMProvider, SessionState
)
from ..services.orchestrator import SessionManager
from ..services.llm_provider import get_provider
from ..core.config import settings
import json

router = APIRouter()

_active_sessions = {}

@router.post("/chat")
async def create_chat(request: CreateChatRequest):
    session_id = f"sess_{uuid4()}"
    provider = request.llm_provider or LLMProvider(settings.DEFAULT_LLM_PROVIDER)
    
    SessionManager.create_session(session_id, provider)
    
    user_message = Message(
        id=f"msg_{uuid4()}",
        role="user",
        content=request.message,
        timestamp=datetime.now().timestamp()
    )
    SessionManager.add_message(session_id, user_message)
    
    return JSONResponse(content={
        "success": True,
        "data": {
            "sessionId": session_id,
            "message": user_message.model_dump()
        }
    })

@router.post("/chat/{session_id}")
async def chat(session_id: str, request: ChatMessage):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    provider = request.llm_provider or session.current_provider
    
    from ..services.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator(session_id, provider)
    
    async def event_callback(event):
        pass
    
    orchestrator.set_event_callback(event_callback)
    
    try:
        async for event in orchestrator.process_message(request.message):
            pass
        
        return JSONResponse(content={"success": True, "data": {"sessionId": session_id}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_sessions():
    sessions = SessionManager.list_sessions()
    return JSONResponse(content={
        "success": True,
        "data": {"sessions": [s.model_dump() for s in sessions]}
    })

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(content={
        "success": True,
        "data": session.model_dump()
    })

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if not SessionManager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(content={"success": True})

@router.get("/health")
async def health_check():
    providers_status = {}
    for provider in ["groq", "openai", "gemini"]:
        key = getattr(settings, f"{provider.upper()}_API_KEY", "")
        providers_status[provider] = bool(key)
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "uptime": "N/A",
        "llmProviders": providers_status
    }