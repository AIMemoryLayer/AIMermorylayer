from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MemoryRecord(BaseModel):
    """
    A single factual or semantic memory stored in the AIMemoryLayer.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the memory"
    )
    owner_id: str = Field(
        ..., description="Unique ID of the human or agent owning this memory"
    )
    content: str = Field(..., description="The raw semantic content of the memory")
    vector: Optional[List[float]] = Field(
        default=None, description="The vector embedding of the content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Custom searchable metadata"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    ttl_seconds: Optional[int] = Field(
        default=None,
        description="Optional Time-To-Live in seconds for ephemeral memories",
    )
