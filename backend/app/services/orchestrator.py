import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Callable, AsyncGenerator
from uuid import uuid4
from ..models.schemas import (
    AgentEvent, AgentEventType, Message, ReasoningStep,
    SessionState, LLMProvider
)
from ..core.config import settings
from .llm_provider import get_provider, BaseLLMProvider
from .tools import get_available_tools, BaseTool

class AgentOrchestrator:
    def __init__(self, session_id: str, llm_provider: LLMProvider = LLMProvider.GROQ):
        self.session_id = session_id
        self.llm_provider = llm_provider
        self.provider_client: Optional[BaseLLMProvider] = None
        self.tools = get_available_tools()
        self.session_state: Optional[SessionState] = None
        self.event_callback: Optional[Callable[[AgentEvent], None]] = None
        
    def set_event_callback(self, callback: Callable[[AgentEvent], None]):
        self.event_callback = callback
    
    async def _emit_event(self, event_type: AgentEventType, data: dict):
        event = AgentEvent(
            type=event_type,
            data=data,
            timestamp=datetime.now().timestamp(),
            id=f"evt_{uuid4()}"
        )
        if self.event_callback:
            self.event_callback(event)
    
    def _get_api_key(self) -> str:
        keys = {
            LLMProvider.GROQ: settings.GROQ_API_KEY,
            LLMProvider.OPENAI: settings.OPENAI_API_KEY,
            LLMProvider.GEMINI: settings.GEMINI_API_KEY,
        }
        return keys.get(self.llm_provider, "")
    
    async def initialize(self):
        api_key = self._get_api_key()
        if not api_key:
            await self._emit_event(AgentEventType.ERROR, {"message": f"No API key for {self.llm_provider}"})
            raise ValueError(f"No API key configured for {self.llm_provider}")
        
        self.provider_client = get_provider(self.llm_provider.value, api_key)
    
    def _build_system_prompt(self) -> str:
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}" for tool in self.tools.values()
        ])
        
        return f"""You are an AI automation agent with access to the following tools:

{tool_descriptions}

To use a tool, respond with a JSON object in this format:
{{
    "tool_call": {{
        "name": "tool_name",
        "arguments": {{"arg1": "value1"}}
    }}
}}

After receiving the tool result, provide your final answer naturally.

Think step-by-step and break down complex problems."""

    async def process_message(self, user_message: str) -> AsyncGenerator[AgentEvent, None]:
        if not self.provider_client:
            await self.initialize()
        
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_message}
        ]
        
        await self._emit_event(AgentEventType.THINKING, {"thought": f"Processing: {user_message[:50]}..."})
        
        iteration = 0
        max_iterations = settings.MAX_ITERATIONS
        
        while iteration < max_iterations:
            iteration += 1
            full_response = ""
            tool_call_detected = False
            
            try:
                async for token in self.provider_client.chat(messages):
                    full_response += token
                    
                    if "tool_call" in full_response.lower() or '"name":' in full_response:
                        tool_call_detected = True
                    
                    await self._emit_event(AgentEventType.STREAMING_TOKEN, {"token": token, "isAssistant": True})
                
                if tool_call_detected:
                    try:
                        import re
                        tool_match = re.search(r'\{[^{]*"tool_call"[^}]*\}', full_response, re.DOTALL)
                        if tool_match:
                            tool_data = json.loads(tool_match.group())
                            tool_info = tool_data.get("tool_call", {})
                            tool_name = tool_info.get("name")
                            tool_args = tool_info.get("arguments", {})
                            
                            if tool_name and tool_name in self.tools:
                                await self._emit_event(AgentEventType.TOOL_CALL, {
                                    "toolName": tool_name,
                                    "toolArgs": tool_args,
                                    "toolCallId": f"tc_{uuid4()}"
                                })
                                
                                result = await self.tools[tool_name].execute(**tool_args)
                                
                                await self._emit_event(AgentEventType.TOOL_RESULT, {
                                    "toolCallId": f"tc_{uuid4()}",
                                    "toolName": tool_name,
                                    "result": result,
                                    "isError": not result.get("success", True)
                                })
                                
                                messages.append({"role": "assistant", "content": full_response})
                                messages.append({"role": "user", "content": f"Tool result: {json.dumps(result)}"})
                                continue
                    except json.JSONDecodeError:
                        pass
                
                await self._emit_event(AgentEventType.DONE, {})
                return
                
            except Exception as e:
                await self._emit_event(AgentEventType.ERROR, {"message": str(e)})
                return
        
        await self._emit_event(AgentEventType.ERROR, {"message": "Max iterations reached"})

class SessionManager:
    _sessions: Dict[str, SessionState] = {}
    
    @classmethod
    def create_session(cls, session_id: str, provider: LLMProvider = LLMProvider.GROQ) -> SessionState:
        session = SessionState(
            id=session_id,
            current_provider=provider
        )
        cls._sessions[session_id] = session
        return session
    
    @classmethod
    def get_session(cls, session_id: str) -> Optional[SessionState]:
        return cls._sessions.get(session_id)
    
    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            return True
        return False
    
    @classmethod
    def list_sessions(cls) -> list[SessionState]:
        return list(cls._sessions.values())
    
    @classmethod
    def add_message(cls, session_id: str, message: Message) -> bool:
        session = cls.get_session(session_id)
        if session:
            session.messages.append(message)
            session.updated_at = datetime.now().timestamp()
            return True
        return False
    
    @classmethod
    def add_reasoning_step(cls, session_id: str, step: ReasoningStep) -> bool:
        session = cls.get_session(session_id)
        if session:
            session.reasoning_chain.append(step)
            return True
        return False
    
    @classmethod
    def get_all_sessions_data(cls) -> Dict[str, dict]:
        return {sid: s.model_dump() for sid, s in cls._sessions.items()}