from datetime import datetime

from pydantic import BaseModel, Field


class Relationship(BaseModel):
    """Relationship between two entities."""

    relationship_id: str

    case_id: str

    source: str
    target: str

    relationship: str

    timestamp: datetime

    source_record: str

    confidence: float = Field(ge=0, le=1)

    weight: float = 1.0

    created_at: datetime