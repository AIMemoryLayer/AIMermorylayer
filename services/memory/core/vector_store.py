from abc import ABC, abstractmethod
from typing import List, Dict
import math
from langchain_community.embeddings import OllamaEmbeddings
from shared.python.models.memory import MemoryRecord


class VectorStoreProvider(ABC):
    """
    Abstract interface for vector database operations.
    Allows seamlessly swapping Pinecone, Qdrant, Milvus, etc.
    """

    @abstractmethod
    async def store(self, memory: MemoryRecord) -> None:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: str, limit: int) -> List[MemoryRecord]:
        pass

    @abstractmethod
    async def search(self, owner_id: str, query: str, limit: int) -> List[MemoryRecord]:
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        pass


class InMemoryVectorStore(VectorStoreProvider):
    """
    Simple in-memory provider for rapid local development and testing.
    Uses Ollama for vector embeddings and basic cosine similarity for search.
    """
    def __init__(self, ollama_model_name: str = "nomic-embed-text", ollama_base_url: str = "http://localhost:11434"):
        self._storage: Dict[str, MemoryRecord] = {}
        # Connect to your local or cloud Ollama instance
        self.embeddings = OllamaEmbeddings(
            model=ollama_model_name,
            base_url=ollama_base_url
        )
        
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)
        
    async def store(self, memory: MemoryRecord) -> None:
        # Generate the dense vector embedding for the content!
        # If running async, we can use aembed_query
        try:
            vector = await self.embeddings.aembed_query(memory.content)
            memory.vector = vector
        except Exception as e:
            # Fallback or log if Ollama is not reachable
            print(f"Warning: Could not connect to Ollama to generate embeddings. {e}")
            memory.vector = []
            
        self._storage[memory.id] = memory

    async def get_by_owner(self, owner_id: str, limit: int) -> List[MemoryRecord]:
        results = [m for m in self._storage.values() if m.owner_id == owner_id]
        # Sort by creation time descending
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results[:limit]

    async def search(self, owner_id: str, query: str, limit: int) -> List[MemoryRecord]:
        # Generate embedding for the search query
        try:
            query_vector = await self.embeddings.aembed_query(query)
        except Exception:
            return [] # Fallback if embeddings are broken

        owner_memories = [m for m in self._storage.values() if m.owner_id == owner_id and m.vector]
        
        # Calculate cosine similarity
        scored_memories = []
        for mem in owner_memories:
            score = self._cosine_similarity(query_vector, mem.vector)
            scored_memories.append((score, mem))
            
        # Sort by highest score first
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [mem for score, mem in scored_memories][:limit]

    async def delete(self, memory_id: str) -> bool:
        if memory_id in self._storage:
            del self._storage[memory_id]
            return True
        return False
