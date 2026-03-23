import lancedb
import os
import numpy as np
from typing import List
from shared.python.models.memory import MemoryRecord
from services.memory.core.vector_store import VectorStoreProvider
from langchain_community.embeddings import OllamaEmbeddings


class LanceVectorStore(VectorStoreProvider):
    """
    Persistent vector store powered by LanceDB.
    Maintains memory context across server restarts.
    """

    def __init__(
        self,
        uri: str = "./data/lance",
        table_name: str = "memories",
        ollama_model: str = "nomic-embed-text",
        ollama_url: str = "http://localhost:11434",
    ):
        os.makedirs(uri, exist_ok=True)
        self.db = lancedb.connect(uri)
        self.table_name = table_name
        self.embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)
        self._table = None

    async def _get_table(self):
        if self._table is not None:
            return self._table

        if self.table_name in self.db.table_names():
            self._table = self.db.open_table(self.table_name)
        else:
            # Create table with initial schema from a blank record if needed
            # For LanceDB, we usually just add data and it infers schema
            pass
        return self._table

    async def store(self, memory: MemoryRecord) -> None:
        # 1. Generate Embedding
        try:
            vector = await self.embeddings.aembed_query(memory.content)
            memory.vector = vector
        except Exception as e:
            print(f"Embedding failed: {e}")
            memory.vector = []

        # 2. Persist to LanceDB
        # Convert UUID to str and ensure vector is a list of floats (or numpy array)
        data = [
            {
                "id": str(memory.id),
                "owner_id": memory.owner_id,
                "content": memory.content,
                "vector": np.array(memory.vector, dtype=np.float32).tolist()
                if memory.vector
                else [],
                "metadata": memory.metadata,
                "created_at": str(memory.created_at),
            }
        ]

        if self.table_name not in self.db.table_names():
            self._table = self.db.create_table(self.table_name, data=data)
        else:
            table = await self._get_table()
            table.add(data)

    async def get_by_owner(self, owner_id: str, limit: int) -> List[MemoryRecord]:
        if self.table_name not in self.db.table_names():
            return []

        table = await self._get_table()
        # Filter by owner_id
        results = (
            table.search().where(f"owner_id = '{owner_id}'").limit(limit).to_list()
        )

        return [self._map_to_record(r) for r in results]

    async def search(self, owner_id: str, query: str, limit: int) -> List[MemoryRecord]:
        if self.table_name not in self.db.table_names():
            return []

        # 1. Embed query
        query_vector = await self.embeddings.aembed_query(query)

        table = await self._get_table()
        # 2. Vector Search + Metadata Filtering
        results = (
            table.search(query_vector)
            .where(f"owner_id = '{owner_id}'")
            .limit(limit)
            .to_list()
        )

        return [self._map_to_record(r) for r in results]

    async def delete(self, memory_id: str) -> bool:
        if self.table_name not in self.db.table_names():
            return False

        table = await self._get_table()
        table.delete(f"id = '{memory_id}'")
        return True

    def _map_to_record(self, raw: dict) -> MemoryRecord:
        return MemoryRecord(
            id=raw["id"],
            owner_id=raw["owner_id"],
            content=raw["content"],
            vector=raw["vector"],
            metadata=raw["metadata"],
            created_at=raw["created_at"],
        )
