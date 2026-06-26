import redis.asyncio as aioredis
import json
from datetime import datetime
from app.config import settings


class AgentMemory:
    """Store and retrieve conversation context across sessions."""

    def __init__(self):
        self.redis = aioredio.from_url(settings.redis_url, decode_responses=True)

    async def load_context(self, session_id: str, limit: int = 3) -> str:
        """Load summary of recent sessions for context."""
        keys = await self.redis.keys("memory:session:*")
        recent = []

        for key in sorted(keys[-limit:], key=lambda x: x.split(":")[-1]):
            data = await self.redis.get(key)
            if data:
                recent.append(json.loads(data))

        if not recent:
            return ""

        context = "Previous conversation summaries:\n"
        for item in recent:
            context += f"- {item.get('summary', 'No summary')}\n"
        return context

    async def save_turn(self, session_id: str, query: str, answer: str):
        """Save conversation turn for future context."""
        # Generate summary using LLM (simplified version)
        summary = f"Query: {query[:100]}... | Answer: {answer[:100]}..."

        await self.redis.setex(
            f"memory:session:{session_id}",
            86400 * 7,  # 7 days TTL
            json.dumps({
                "session_id": session_id,
                "query": query,
                "answer": answer,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
            })
        )