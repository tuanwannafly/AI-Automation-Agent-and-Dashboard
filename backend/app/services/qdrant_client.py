from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from app.config import settings
import hashlib

embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
qdrant_client = AsyncQdrantClient(url=settings.qdrant_url)

COLLECTION_NAME = "documents"
VECTOR_SIZE = 384  # BAAI/bge-small-en-v1.5 embedding size


async def ensure_collection():
    """Ensure the documents collection exists."""
    collections = await qdrant_client.get_collections()
    if COLLECTION_NAME not in [c.name for c in collections.collections]:
        await qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


async def index_document(file_id: str, text: str, source: str):
    """Index document text into Qdrant."""
    await ensure_collection()

    # Chunk text
    chunks = _chunk_text(text, chunk_size=500)

    points = []
    for i, chunk in enumerate(chunks):
        vector = embedder.encode(chunk).tolist()
        point_id = int(hashlib.md5(f"{file_id}_{i}".encode()).hexdigest(), 16) % (10 ** 18)
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": chunk,
                    "source": source,
                    "file_id": file_id,
                    "chunk_index": i,
                },
            )
        )

    if points:
        await qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks if chunks else [""]