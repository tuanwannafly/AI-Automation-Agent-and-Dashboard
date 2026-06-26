import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from uuid import uuid4
from datetime import datetime
from ..models.schemas import (
    AgentEvent, AgentEventType, Message, ReasoningStep,
    SessionState, LLMProvider
)
from ..services.orchestrator import SessionManager, AgentOrchestrator
from ..core.config import settings

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    session = SessionManager.get_session(session_id)
    if not session:
        SessionManager.create_session(session_id)
        session = SessionManager.get_session(session_id)
    
    orchestrator = AgentOrchestrator(session_id, session.current_provider)
    
    async def event_callback(event: AgentEvent):
        await manager.send_personal_message({
            "type": event.type.value,
            "data": event.data,
            "timestamp": event.timestamp,
            "id": event.id
        }, session_id)
        
        if event.type == AgentEventType.THINKING:
            SessionManager.add_reasoning_step(session_id, ReasoningStep(
                id=event.id,
                type="thinking",
                content=event.data.get("thought", ""),
                timestamp=event.timestamp
            ))
        elif event.type == AgentEventType.TOOL_CALL:
            SessionManager.add_reasoning_step(session_id, ReasoningStep(
                id=event.id,
                type="tool_call",
                content=f"Calling {event.data.get('toolName', 'unknown')}",
                data=event.data,
                timestamp=event.timestamp
            ))
        elif event.type == AgentEventType.TOOL_RESULT:
            SessionManager.add_reasoning_step(session_id, ReasoningStep(
                id=event.id,
                type="tool_result",
                content=str(event.data.get("result", "")),
                data=event.data,
                timestamp=event.timestamp,
            ))
    
    orchestrator.set_event_callback(event_callback)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                if message_data.get("type") == "PING":
                    await manager.send_personal_message({"type": "PONG"}, session_id)
                    continue
                if message_data.get("type") == "CHAT":
                    user_message = Message(
                        id=f"msg_{uuid4()}",
                        role="user",
                        content=message_data.get("content", ""),
                        timestamp=datetime.now().timestamp()
                    )
                    SessionManager.add_message(session_id, user_message)
                    
                    async for event in orchestrator.process_message(message_data.get("content", "")):
                        pass
            except json.JSONDecodeError:
                user_message = Message(
                    id=f"msg_{uuid4()}",
                    role="user",
                    content=data,
                    timestamp=datetime.now().timestamp()
                )
                SessionManager.add_message(session_id, user_message)
                
                async for event in orchestrator.process_message(data):
                    pass
                    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_personal_message({
            "type": "ERROR",
            "data": {"message": str(e)},
            "timestamp": datetime.now().timestamp(),
            "id": f"evt_{uuid4()}"
        }, session_id)