from datetime import datetime

from pydantic import BaseModel, Field


class Relationship(BaseModel):
    """A relationship associated with a specific case."""

    case_id: str
    source: str
    relationship: str
    target: str
    timestamp: datetime
    source_record: str
    confidence: float = Field(ge=0, le=1)
