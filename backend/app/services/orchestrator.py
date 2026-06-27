import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Callable, List
from uuid import uuid4
from ..models.schemas import (
    AgentEvent, AgentEventType, Message, ReasoningStep,
    SessionState, LLMProvider
)
from ..core.config import settings
from .llm_provider import get_provider, BaseLLMProvider
from .tools import get_available_tools, BaseTool
from .rag import rag_engine

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
            await self.event_callback(event)
    
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
    
    def _build_system_prompt(self, rag_context: str = "") -> str:
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}" for tool in self.tools.values()
        ])
        
        rag_section = ""
        if rag_context:
            rag_section = f"""

You have access to the following knowledge from uploaded documents. Use this context to answer questions when relevant:

{rag_context}
"""
        
        return f"""You are an AI automation agent with access to the following tools:

{tool_descriptions}{rag_section}

To use a tool, respond with a JSON object in this format:
{{
    "tool_call": {{
        "name": "tool_name",
        "arguments": {{"arg1": "value1"}}
    }}
}}

After receiving the tool result, provide your final answer naturally.

Think step-by-step and break down complex problems."""

    async def process_message(self, user_message: str, file_ids: Optional[List[str]] = None) -> None:
        print(f"[Orchestrator] Starting process_message with: {user_message[:50]}...")
        if not self.provider_client:
            print(f"[Orchestrator] Initializing provider client...")
            await self.initialize()
            print(f"[Orchestrator] Provider client initialized")
        
        # Query RAG engine for relevant context ONLY from files belonging to
        # the current conversation. This avoids older uploaded documents
        # acting as a global "source of truth" for every new chat.
        rag_context = ""
        try:
            if file_ids:
                print(f"[Orchestrator] Querying RAG for {len(file_ids)} session file(s)...")
                rag_context = rag_engine.query_with_context(user_message, limit=3, file_ids=file_ids)
                if rag_context and rag_context != "No relevant documents found.":
                    print(f"[Orchestrator] RAG context retrieved: {len(rag_context)} chars")
                else:
                    rag_context = ""
        except Exception as rag_error:
            print(f"[Orchestrator] RAG query error (non-fatal): {rag_error}")
            rag_context = ""
        
        messages = [
            {"role": "system", "content": self._build_system_prompt(rag_context)},
            {"role": "user", "content": user_message}
        ]
        
        print(f"[Orchestrator] Emitting THINKING event...")
        await self._emit_event(AgentEventType.THINKING, {"thought": f"Processing: {user_message[:50]}..."})
        print(f"[Orchestrator] THINKING event emitted")
        
        iteration = 0
        max_iterations = settings.MAX_ITERATIONS
        
        while iteration < max_iterations:
            iteration += 1
            full_response = ""
            tool_call_detected = False
            
            try:
                print(f"[Orchestrator] Starting LLM chat stream (iteration {iteration})...")
                async for token in self.provider_client.chat(messages):
                    print(f"[Orchestrator] Received token: {token[:20] if len(token) > 20 else token}")
                    full_response += token
                    
                    if "tool_call" in full_response.lower() or '"name":' in full_response:
                        tool_call_detected = True
                    
                    await self._emit_event(AgentEventType.STREAMING_TOKEN, {"token": token, "isAssistant": True})
                
                print(f"[Orchestrator] LLM stream complete, full_response: {full_response[:100]}...")
                
                if tool_call_detected:
                    try:
                        import re
                        # Find all JSON-like blocks and try to parse them
                        json_blocks = re.findall(r'\{.*?\}', full_response, re.DOTALL)
                        tool_data = None
                        for block in json_blocks:
                            try:
                                parsed = json.loads(block)
                                if "tool_call" in parsed:
                                    tool_data = parsed
                                    break
                            except json.JSONDecodeError:
                                continue
                        
                        # If simple blocks didn't work, try extracting from first { to last }
                        if not tool_data:
                            first_brace = full_response.find('{')
                            last_brace = full_response.rfind('}')
                            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                                candidate = full_response[first_brace:last_brace + 1]
                                try:
                                    parsed = json.loads(candidate)
                                    if "tool_call" in parsed:
                                        tool_data = parsed
                                except json.JSONDecodeError:
                                    pass
                        
                        if tool_data:
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
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"[Orchestrator] Tool call parsing error: {e}")
                
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