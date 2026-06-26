from app.agent.runner import AgentRunner
from app.api.websocket import ws_manager
from app.models.chat import ChatRequest, ChatResponse
from fastapi import APIRouter, BackgroundTasks
import uuid

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """Create a new chat session and start agent in background."""
    session_id = str(uuid.uuid4())
    runner = AgentRunner(session_id=session_id, ws_manager=ws_manager)

    # Run agent in background (non-blocking)
    background_tasks.add_task(runner.run, request)

    return ChatResponse(
        session_id=session_id,
        ws_url=f"ws://localhost:8000/ws/{session_id}",
        status="running"
    )
from fastapi import APIRouter

router = APIRouter()
