from app.agent.tools.registry import tool_registry
from app.llm.groq import complete_groq
from typing import List
import hashlib
import json

# Simple in-memory cache
_summary_cache: dict = {}


@tool_registry.register(
    name="summarizer",
    description="Tóm tắt văn bản dài (>2000 từ) sử dụng map-reduce. Kết quả được cache theo nội dung."
)
async def summarizer(text: str, max_length: int = 500) -> dict:
    """Summarize long text using map-reduce with LLM."""
    # Cache check
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in _summary_cache:
        return _summary_cache[cache_key]

    # Map: chunk → summarize each chunk
    chunks = _chunk_text(text, chunk_size=3000)
    chunk_summaries = []

    for i, chunk in enumerate(chunks):
        messages = [
            {"role": "system", "content": "You are a precise summarizer. Summarize the given text concisely."},
            {"role": "user", "content": f"Summarize this text segment:\n\n{chunk}"}
        ]
        summary = await complete_groq(messages)
        chunk_summaries.append(summary)

    # Reduce: combine summaries
    if len(chunk_summaries) > 1:
        combined = "\n\n".join(chunk_summaries)
        reduce_messages = [
            {"role": "system", "content": "Combine these summaries into one coherent summary."},
            {"role": "user", "content": combined}
        ]
        final_summary = await complete_groq(reduce_messages)
    else:
        final_summary = chunk_summaries[0] if chunk_summaries else ""

    result = {
        "summary": final_summary,
        "original_length": len(text),
        "summary_length": len(final_summary),
        "chunks_processed": len(chunks),
    }

    _summary_cache[cache_key] = result
    return result


def _chunk_text(text: str, chunk_size: int = 3000) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks