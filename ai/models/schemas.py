from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORGANIZATION"
    VEHICLE = "VEHICLE"
    PHONE = "PHONE"
    DATE = "DATE"


class Entity(BaseModel):
    entity_id: Optional[str] = None
    entity_type: EntityType
    name: str

    source: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0
    )

    start_char: Optional[int] = None
    end_char: Optional[int] = None


class Relationship(BaseModel):
    source: str
    relationship: str
    target: str

    timestamp: Optional[str] = None
    source_record: Optional[str] = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0
    )


class Event(BaseModel):
    event_type: str

    timestamp: Optional[str] = None

    participants: list[str] = Field(
        default_factory=list
    )

    location: Optional[str] = None

    amount: Optional[float] = None

    source_record: Optional[str] = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0
    )


class ExtractionResult(BaseModel):
    source_record: str
    source_text: str

    entities: list[Entity] = Field(
        default_factory=list
    )

    relationships: list[Relationship] = Field(
        default_factory=list
    )

    events: list[Event] = Field(
        default_factory=list
    )

class CDRRecord(BaseModel):
    caller: str
    receiver: str
    timestamp: str
    duration: float = Field(ge=0.0)
    source_record: str


class FinancialTransaction(BaseModel):
    sender: str
    receiver: str
    amount: float = Field(ge=0.0)
    timestamp: str
    source_record: str