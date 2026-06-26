from fastapi import APIRouter
from app.models.chat import SessionState
import uuid

router = APIRouter()

# In-memory session store (replace with Redis in Phase 3)
session_store: dict[str, SessionState] = {}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session by ID."""
    if session_id not in session_store:
        return {"error": "Session not found"}
    return session_store[session_id]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete session by ID."""
    if session_id in session_store:
        del session_store[session_id]
    return {"deleted": True}


@router.post("/sessions")
async def create_session():
    """Create a new empty session."""
    session_id = str(uuid.uuid4())
    session_store[session_id] = SessionState(session_id=session_id)
    return {"session_id": session_id}