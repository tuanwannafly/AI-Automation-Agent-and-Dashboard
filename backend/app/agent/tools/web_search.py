import httpx
from duckduckgo_search import AsyncDDGS
from app.agent.tools.registry import tool_registry
from app.config import settings
from typing import List


@tool_registry.register(
    name="web_search",
    description="Tìm kiếm thông tin trên internet. Dùng khi cần thông tin thời gian thực hoặc kiến thức nằm ngoài tài liệu đã upload."
)
async def web_search(query: str, max_results: int = 5) -> List[dict]:
    """DuckDuckGo với fallback sang Serper nếu rate limit."""
    try:
        return await _ddg_search(query, max_results)
    except Exception as e:
        if settings.serper_api_key:
            return await _serper_search(query, max_results)
        raise e


async def _ddg_search(query: str, max_results: int) -> List[dict]:
    async with AsyncDDGS() as ddgs:
        results = []
        async for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
            if len(results) >= max_results:
                break
        return results


async def _serper_search(query: str, max_results: int) -> List[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://google.serper.dev/search",
            json={"q": query, "num": max_results},
            headers={"X-API-KEY": settings.serper_api_key},
            timeout=10,
        )
        data = response.json()
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
            for item in data.get("organic", [])[:max_results]
        ]