from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """An entity associated with a specific case."""

    case_id: str
    entity_id: str
    entity_type: str
    name: str

    source: str
    source_record: Optional[str] = None

    confidence: float = Field(ge=0, le=1)

    created_at: datetime
    updated_at: datetime
