from groq import AsyncGroq
from app.config import settings
from typing import AsyncGenerator

client = AsyncGroq(api_key=settings.groq_api_key)


async def stream_groq(
    messages: list[dict],
    model: str = "llama3-70b-8192",
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """Yield tokens từng token."""
    stream = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
        temperature=temperature,
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token


async def complete_groq(messages: list[dict], model: str = "llama3-70b-8192") -> str:
    """Non-streaming complete."""
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=False,
    )
    return response.choices[0].message.content