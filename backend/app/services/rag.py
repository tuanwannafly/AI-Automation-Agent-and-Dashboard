from typing import List, Dict, Optional
from uuid import uuid4
import json

class ChromaVectorStore:
    """Simple in-memory vector store for RAG (fallback if chromadb not available)"""
    
    def __init__(self):
        self.collections: Dict[str, List[Dict]] = {}
    
    def create_collection(self, name: str) -> bool:
        if name not in self.collections:
            self.collections[name] = []
            return True
        return False
    
    def add_documents(self, collection: str, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        if collection not in self.collections:
            self.create_collection(collection)
        
        for i, doc in enumerate(documents):
            doc_id = ids[i] if ids else f"doc_{uuid4()}"
            metadata = metadatas[i] if metadatas else {}
            self.collections[collection].append({
                "id": doc_id,
                "content": doc,
                "metadata": metadata
            })
    
    def query(self, collection: str, query: str, limit: int = 5) -> List[Dict]:
        if collection not in self.collections:
            return []
        
        docs = self.collections[collection]
        query_lower = query.lower()
        
        scored = []
        for doc in docs:
            score = self._simple_similarity(query_lower, doc["content"].lower())
            scored.append((score, doc))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        results = []
        for score, doc in scored[:limit]:
            results.append({**doc, "score": score})
        return results
    
    _STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
        "be", "been", "being", "to", "of", "in", "on", "at", "for", "with",
        "by", "from", "as", "this", "that", "these", "those", "it", "its",
        "what", "which", "who", "whom", "whose", "when", "where", "why",
        "how", "do", "does", "did", "can", "could", "should", "would",
        "will", "shall", "may", "might", "must", "have", "has", "had",
        "i", "you", "he", "she", "we", "they", "me", "him", "her", "us",
        "them", "my", "your", "his", "our", "their", "tell", "about",
        "give", "me", "please", "show", "summarize",
    }
    
    def _simple_similarity(self, query: str, text: str) -> float:
        import re
        query_words = {w for w in re.findall(r"\w+", query.lower()) if w not in self._STOPWORDS}
        text_words = {w for w in re.findall(r"\w+", text.lower()) if w not in self._STOPWORDS}
        if not query_words or not text_words:
            return 0.0
        intersection = query_words & text_words
        return len(intersection) / len(query_words | text_words)

class RAGEngine:
    """Retrieval Augmented Generation Engine"""
    
    MIN_RELEVANCE_THRESHOLD = 0.05
    
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.indexed_files: Dict[str, Dict] = {}
    
    def index_file(self, file_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        try:
            chunks = self._chunk_text(content, chunk_size=500, overlap=50)
            
            chunk_ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_metadatas = [
                {"file_id": file_id, "chunk": i, "total_chunks": len(chunks), **(metadata or {})}
                for i in range(len(chunks))
            ]
            
            self.vector_store.add_documents(
                collection="documents",
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            self.indexed_files[file_id] = {
                "file_id": file_id,
                "chunks_count": len(chunks),
                "metadata": metadata or {},
                "indexed_at": json.dumps({"_type": "timestamp"})
            }
            
            return True
        except Exception as e:
            print(f"Error indexing file {file_id}: {e}")
            return False
    
    def query(self, query: str, limit: int = 5, file_id: Optional[str] = None, file_ids: Optional[List[str]] = None) -> List[Dict]:
        # Scope to specific files (session-scoped RAG). This prevents previously
        # uploaded documents from leaking into a new conversation.
        allowed_ids = None
        if file_ids is not None:
            allowed_ids = set(file_ids)
        elif file_id is not None:
            allowed_ids = {file_id}
        
        # Fetch a wide candidate pool so ranking stays meaningful even for
        # generic queries like "summarize this document".
        pool_limit = limit * 4 if allowed_ids is not None else limit * 2
        results = self.vector_store.query("documents", query, limit=pool_limit)
        
        if allowed_ids is not None:
            results = [r for r in results if r["metadata"].get("file_id") in allowed_ids]
            # When files are explicitly attached, the user wants them read regardless
            # of keyword overlap, so return the top-ranked chunks without a cutoff.
            return results[:limit]
        else:
            # No explicit file attachment: apply a relevance cutoff to avoid noise.
            results = [r for r in results if r.get("score", 0) >= self.MIN_RELEVANCE_THRESHOLD]
            return results[:limit]
    
    def query_with_context(self, query: str, limit: int = 5, file_id: Optional[str] = None, file_ids: Optional[List[str]] = None) -> str:
        results = self.query(query, limit, file_id=file_id, file_ids=file_ids)
        
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            file_id = result["metadata"].get("file_id", "unknown")
            context_parts.append(f"[Source {i} - File: {file_id}]\n{result['content']}")
        
        return "\n\n".join(context_parts)
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if len(chunk) > overlap:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks if chunks else [text]
    
    def get_indexed_files(self) -> List[Dict]:
        return list(self.indexed_files.values())
    
    def delete_file(self, file_id: str) -> bool:
        if file_id not in self.indexed_files:
            return False
        
        if "documents" in self.vector_store.collections:
            self.vector_store.collections["documents"] = [
                doc for doc in self.vector_store.collections["documents"]
                if doc["metadata"].get("file_id") != file_id
            ]
        
        del self.indexed_files[file_id]
        return True

rag_engine = RAGEngine()