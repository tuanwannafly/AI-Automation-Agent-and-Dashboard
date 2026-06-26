from app.agent.graph import agent_graph
from app.agent.state import AgentState
from app.api.websocket import ConnectionManager
from app.models.chat import ChatRequest
import asyncio
import time


class AgentRunner:
    def __init__(self, session_id: str, ws_manager: ConnectionManager):
        self.session_id = session_id
        self.ws_manager = ws_manager

    async def emit(self, event: dict):
        """Gửi event ra WebSocket."""
        await self.ws_manager.send_event(self.session_id, event)

    async def run(self, request: ChatRequest):
        start_time = time.time()

        # Initial state
        initial_state: AgentState = {
            "user_query": request.message,
            "uploaded_files": request.file_ids or [],
            "workflow_config": None,
            "plan": [],
            "tool_calls": [],
            "tool_results": [],
            "current_step": 0,
            "max_iterations": 5,
            "final_answer": "",
            "reasoning_chain": [],
            "session_id": self.session_id,
            "llm_provider": request.llm_provider or "groq",
            "tokens_used": 0,
            "execution_time_ms": 0,
            "error": None,
        }

        await self.emit({"type": "THINKING", "content": "Đang phân tích câu hỏi...", "step": 0})

        try:
            # Stream through LangGraph nodes
            async for event in agent_graph.astream(initial_state):
                # Emit relevant events based on state changes
                for node_name, node_output in event.items():
                    await self._emit_node_events(node_name, node_output)

            # Final state
            final_state = await agent_graph.ainvoke(initial_state)
            elapsed = int((time.time() - start_time) * 1000)

            await self.emit({
                "type": "DONE",
                "final_answer": final_state.get("final_answer", ""),
                "reasoning_chain": final_state.get("reasoning_chain", []),
                "total_tokens": final_state.get("tokens_used", 0),
                "total_time_ms": elapsed,
            })

        except Exception as e:
            await self.emit({
                "type": "ERROR",
                "message": str(e),
                "recoverable": False
            })

    async def _emit_node_events(self, node_name: str, state: dict):
        """Map LangGraph node output → WebSocket events."""
        reasoning_chain = state.get("reasoning_chain", [])
        if reasoning_chain:
            latest = reasoning_chain[-1]
            event_type = latest.get("type", "THINKING")

            if event_type == "THINKING":
                await self.emit({
                    "type": "THINKING",
                    "content": latest.get("content", ""),
                    "step": latest.get("step", 0),
                })
            elif event_type == "TOOL_USE":
                await self.emit({
                    "type": "TOOL_CALL",
                    "tool": latest.get("tool", ""),
                    "input": {},
                })
                await self.emit({
                    "type": "TOOL_RESULT",
                    "tool": latest.get("tool", ""),
                    "output": latest.get("result_preview", ""),
                    "duration_ms": 0,
                })