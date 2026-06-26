from fastapi import APIRouter
from app.models.chat import SessionState
from app.services.session import SessionManager
import uuid

router = APIRouter()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session by ID from Redis."""
    session = await SessionManager.get_state(session_id)
    if not session:
        return {"error": "Session not found"}
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete session by ID from Redis."""
    await SessionManager.delete_session(session_id)
    return {"deleted": True}


@router.post("/sessions")
async def create_session():
    """Create a new empty session."""
    session_id = str(uuid.uuid4())
    session_store = {"session_id": session_id}
    await SessionManager.save_state(session_id, session_store)
    return {"session_id": session_id}