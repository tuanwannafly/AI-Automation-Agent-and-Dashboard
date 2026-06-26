from app.config import settings
from typing import Literal

LLMProvider = Literal["groq", "openai", "gemini"]


async def complete(
    messages: list[dict],
    provider: LLMProvider = "groq",
    **kwargs
) -> str:
    """Route to appropriate LLM provider."""
    if provider == "groq":
        from app.llm.groq import complete_groq
        return await complete_groq(messages, **kwargs)
    elif provider == "openai":
        from app.llm.openai import complete_openai
        return await complete_openai(messages, **kwargs)
    elif provider == "gemini":
        from app.llm.gemini import complete_gemini
        return await complete_gemini(messages, **kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def stream(provider: LLMProvider = "groq", **kwargs):
    """Stream from appropriate LLM provider."""
    if provider == "groq":
        from app.llm.groq import stream_groq
        return stream_groq(**kwargs)
    elif provider == "openai":
        from app.llm.openai import stream_openai
        return stream_openai(**kwargs)
    elif provider == "gemini":
        from app.llm.gemini import stream_gemini
        return stream_gemini(**kwargs)