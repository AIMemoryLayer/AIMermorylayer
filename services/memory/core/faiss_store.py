import os
import faiss
import numpy as np
import pickle
from typing import List
from shared.python.models.memory import MemoryRecord
from services.memory.core.vector_store import VectorStoreProvider
from langchain_community.embeddings import OllamaEmbeddings


class FaissVectorStore(VectorStoreProvider):
    """
    Lightweight persistent vector store powered by FAISS and Pickle.
    Guaranteed to work on Windows without complex dependency hangs.
    """

    def __init__(
        self,
        base_path: str = "./data/faiss",
        ollama_model: str = "nomic-embed-text",
        ollama_url: str = "http://localhost:11434",
    ):
        self.base_path = base_path
        self.index_path = os.path.join(base_path, "index.faiss")
        self.meta_path = os.path.join(base_path, "metadata.pkl")
        os.makedirs(base_path, exist_ok=True)

        self.embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)
        self.dimension = 768  # nomic-embed-text dimension

        # Initialize FAISS index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.records = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.records = []

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.records, f)

    async def store(self, memory: MemoryRecord) -> None:
        # 1. Generate Embedding
        try:
            vector = await self.embeddings.aembed_query(memory.content)
            memory.vector = vector
        except Exception as e:
            print(f"Embedding failed: {e}")
            memory.vector = [0.0] * self.dimension

        # 2. Add to FAISS
        vec_np = np.array([memory.vector], dtype=np.float32)
        self.index.add(vec_np)

        # 3. Store Metadata
        self.records.append(memory)
        self._save()

    async def get_by_owner(self, owner_id: str, limit: int) -> List[MemoryRecord]:
        return [r for r in self.records if r.owner_id == owner_id][-limit:]

    async def search(self, owner_id: str, query: str, limit: int) -> List[MemoryRecord]:
        # 1. Embed query
        query_vec = await self.embeddings.aembed_query(query)
        query_np = np.array([query_vec], dtype=np.float32)

        # 2. Search FAISS
        distances, indices = self.index.search(query_np, len(self.records))

        # 3. Filter by owner and limit
        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            record = self.records[idx]
            if record.owner_id == owner_id:
                results.append(record)
                if len(results) >= limit:
                    break
        return results

    async def delete(self, memory_id: str) -> bool:
        # FAISS IndexFlatL2 doesn't support easy deletion by ID without rebuilding
        # For Day 2, we will filter in-memory and mark for rebuild later if needed
        # Or just use a simple flag
        initial_len = len(self.records)
        self.records = [r for r in self.records if str(r.id) != memory_id]
        if len(self.records) != initial_len:
            # Rebuild index for consistency
            self.index = faiss.IndexFlatL2(self.dimension)
            if self.records:
                vectors = np.array([r.vector for r in self.records], dtype=np.float32)
                self.index.add(vectors)
            self._save()
            return True
        return False
