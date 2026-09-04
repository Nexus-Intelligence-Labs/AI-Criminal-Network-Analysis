from datetime import datetime

from pydantic import BaseModel, Field


class Relationship(BaseModel):
    source: str
    relationship: str
    target: str
    timestamp: datetime
    source_record: str
    confidence: float = Field(ge=0, le=1)
