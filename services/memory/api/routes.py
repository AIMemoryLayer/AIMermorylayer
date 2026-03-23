from fastapi import APIRouter, HTTPException
from typing import List, Optional
from shared.python.models.memory import MemoryRecord
from core.vector_store import VectorStoreProvider
from core.faiss_store import FaissVectorStore
import uuid

router = APIRouter(tags=["Memories"])

# Use FAISS for lightweight persistence on Windows
vector_store: VectorStoreProvider = FaissVectorStore()


@router.post("/memories", response_model=MemoryRecord)
async def create_memory(memory: MemoryRecord):
    """
    Ingest a new memory into the semantic database.
    If no ID is provided, one will be generated.
    """
    if not memory.id:
        memory.id = str(uuid.uuid4())

    # Normally we would generate the vector embedding here before storing
    # For now, we store the raw record.
    await vector_store.store(memory)
    return memory


@router.get("/memories/{owner_id}", response_model=List[MemoryRecord])
async def get_memories(
    owner_id: str,
    limit: int = 10,
    query: Optional[str] = None,
    importance: Optional[str] = None,
    type: Optional[str] = None,
):
    """
    Retrieve memories for a specific owner (user/agent).
    If a query is provided, performs a semantic search with cosine similarity.
    Supports optional metadata filters (importance, type).
    """
    filters = {}
    if importance:
        filters["importance"] = importance
    if type:
        filters["type"] = type

    if query:
        return await vector_store.search(owner_id, query, limit, filters=filters)

    memories = await vector_store.get_by_owner(owner_id, limit)
    # Apply filters to non-semantic retrieval too
    if filters:
        memories = [
            m
            for m in memories
            if all(m.metadata.get(k) == v for k, v in filters.items())
        ]

    return memories


@router.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Delete a specific memory by ID.
    Ensures right-to-be-forgotten compliance.
    """
    success = await vector_store.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "success", "deleted_id": memory_id}
