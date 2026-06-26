from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def complete_openai(messages: list[dict], model: str = "gpt-4o") -> str:
    """Non-streaming complete using OpenAI."""
    response = await client.chat.completions.create(
        messages=messages, model=model, stream=False
    )
    return response.choices[0].message.content


async def stream_openai(messages: list[dict], model: str = "gpt-4o"):
    """Stream tokens using OpenAI."""
    stream = await client.chat.completions.create(
        messages=messages, model=model, stream=True
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token