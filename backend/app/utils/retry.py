import asyncio
from functools import wraps


def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for exponential backoff retry."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    raise
        return wrapper
    return decorator