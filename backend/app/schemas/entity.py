from pydantic import BaseModel, Field


class Entity(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    source: str
    confidence: float = Field(ge=0, le=1)
