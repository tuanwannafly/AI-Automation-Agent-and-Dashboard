from qdrant_client import AsyncQdrantClient
from app.agent.tools.registry import tool_registry
from app.config import settings
from sentence_transformers import SentenceTransformer
from typing import List

# Embedding model
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
qdrant = AsyncQdrantClient(url=settings.qdrant_url)


@tool_registry.register(
    name="rag_search",
    description="Tìm kiếm tài liệu đã upload vào knowledge base (Qdrant). Dùng khi user hỏi về nội dung file đã index."
)
async def rag_search(
    query: str,
    collection: str = "documents",
    top_k: int = 5,
) -> List[dict]:
    """Search Qdrant vector database."""
    try:
        # Embed query
        vector = embedder.encode(query).tolist()

        # Search Qdrant
        results = await qdrant.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
        )

        return [
            {
                "content": hit.payload.get("text", "") if hit.payload else "",
                "source": hit.payload.get("source", "unknown") if hit.payload else "",
                "score": round(hit.score, 4),
                "metadata": hit.payload,
            }
            for hit in results
        ]
    except Exception as e:
        return [{"error": str(e), "content": "", "source": "", "score": 0}]