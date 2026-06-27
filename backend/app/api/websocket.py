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
    try:
        origin = websocket.headers.get("origin")
        print(f"[WebSocket] Connection request from origin: {origin}, session: {session_id}")
        await websocket.accept()
        print(f"[WebSocket] Connection accepted: {session_id}")
        print(f"[WebSocket] Connection accepted: {session_id}")
        
        manager.active_connections[session_id] = websocket
        print(f"[WebSocket] Added to manager: {session_id}, total connections: {len(manager.active_connections)}")
        
        session = SessionManager.get_session(session_id)
        if not session:
            print(f"[WebSocket] Creating new session: {session_id}")
            SessionManager.create_session(session_id)
            session = SessionManager.get_session(session_id)
        
        print(f"[WebSocket] Session loaded: {session.id}")
        
        orchestrator = AgentOrchestrator(session_id, session.current_provider)
        print(f"[WebSocket] Orchestrator created")
        
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
                print(f"[WebSocket] Waiting for message from {session_id}")
                data = await websocket.receive_text()
                print(f"[WebSocket] Received message: {data[:50]}...")
                
                try:
                    message_data = json.loads(data)
                    print(f"[WebSocket] Parsed message data: type={message_data.get('type')}")
                    if message_data.get("type") == "PING":
                        print(f"[WebSocket] Received PING, sending PONG")
                        await manager.send_personal_message({"type": "PONG"}, session_id)
                        continue
                    if message_data.get("type") == "CHAT":
                        print(f"[WebSocket] Received CHAT message, content: {message_data.get('content', '')[:50]}")
                        file_ids = message_data.get("fileIds") or message_data.get("file_ids") or []
                        user_message = Message(
                            id=f"msg_{uuid4()}",
                            role="user",
                            content=message_data.get("content", ""),
                            timestamp=datetime.now().timestamp()
                        )
                        SessionManager.add_message(session_id, user_message)
                        print(f"[WebSocket] Starting orchestrator processing (file_ids={file_ids})...")
                        
                        try:
                            print(f"[WebSocket] Awaiting orchestrator processing...")
                            await orchestrator.process_message(message_data.get("content", ""), file_ids=file_ids)
                            print(f"[WebSocket] Orchestrator processing complete")
                        except Exception as orch_error:
                            print(f"[WebSocket] Orchestrator error: {orch_error}")
                            import traceback
                            traceback.print_exc()
                            await manager.send_personal_message({
                                "type": "error",
                                "data": {"message": str(orch_error)}
                            }, session_id)
                except json.JSONDecodeError:
                    user_message = Message(
                        id=f"msg_{uuid4()}",
                        role="user",
                        content=data,
                        timestamp=datetime.now().timestamp()
                    )
                    SessionManager.add_message(session_id, user_message)
                    
                    await orchestrator.process_message(data, file_ids=[])
                    
        except WebSocketDisconnect:
            print(f"[WebSocket] Disconnected: {session_id}")
            manager.disconnect(session_id)
        except Exception as e:
            print(f"[WebSocket] Error for {session_id}: {e}")
            manager.disconnect(session_id)
            raise
            
    except Exception as e:
        print(f"[WebSocket] Fatal error: {e}")
        raise