from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active[session_id] = ws

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)

    async def send_event(self, session_id: str, event: dict):
        if ws := self.active.get(session_id):
            await ws.send_text(json.dumps(event))


ws_manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "PING":
                await ws_manager.send_event(session_id, {"type": "PONG"})
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)