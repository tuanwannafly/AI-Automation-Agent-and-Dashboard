import asyncio
import sys
import os
import io

# Ensure UTF-8 output on Windows so streamed tokens with non-cp1252 chars
# (emoji, curly quotes, etc.) don't crash with UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.orchestrator import AgentOrchestrator, SessionManager
from app.models.schemas import AgentEvent, AgentEventType, LLMProvider

async def main():
    session_id = "test_session_001"
    SessionManager.create_session(session_id, LLMProvider.GROQ)
    orchestrator = AgentOrchestrator(session_id, LLMProvider.GROQ)

    events_received = []

    async def event_callback(event: AgentEvent):
        print(f"  [EVENT] type={event.type}, data={str(event.data)[:300]}")
        events_received.append(event)

    orchestrator.set_event_callback(event_callback)

    print("=" * 60)
    print("Testing orchestrator.process_message with a simple prompt")
    print("=" * 60)

    try:
        result = await orchestrator.process_message("Hello, what is 2+2?")
        print(f"\n[RESULT] process_message returned: {result}")
        print(f"[RESULT] type of return: {type(result)}")
    except Exception as e:
        print(f"\n[ERROR] Exception during process_message: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n[SUMMARY] Total events received: {len(events_received)}")
    for evt in events_received:
        print(f"  - {evt.type}: {str(evt.data)[:80]}")

if __name__ == "__main__":
    asyncio.run(main())