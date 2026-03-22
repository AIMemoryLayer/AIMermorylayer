from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryEvent(BaseModel):
    """
    An event representing an action taken on the memory layer.
    """

    event_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the event"
    )
    event_type: str = Field(
        ..., description="Type of event, e.g., 'memory.created', 'memory.forgotten'"
    )
    owner_id: str = Field(..., description="The human or agent this event belongs to")
    payload: Dict[str, Any] = Field(..., description="Data associated with the event")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event occurred",
    )
