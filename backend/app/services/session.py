import redis.asyncio as aioredis
import json
from app.config import settings


class SessionManager:
    @staticmethod
    async def save_state(session_id: str, state: dict, ttl: int = 3600):
        """Save session state to Redis with TTL."""
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(state, default=str)
        )

    @staticmethod
    async def get_state(session_id: str) -> dict | None:
        """Get session state from Redis."""
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        data = await redis_client.get(f"session:{session_id}")
        return json.loads(data) if data else None

    @staticmethod
    async def delete_session(session_id: str):
        """Delete session from Redis."""
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.delete(f"session:{session_id}")