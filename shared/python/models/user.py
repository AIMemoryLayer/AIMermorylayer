from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """
    The current active context for a user or agent querying the memory layer.
    """

    owner_id: str = Field(..., description="Unique ID of the human or agent")
    session_id: Optional[str] = Field(
        default=None, description="Identifier for a specific conversation/session"
    )
    active_personas: List[str] = Field(
        default_factory=list, description="Personas active in the current context"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict, description="User or agent preferences"
    )
