from datetime import datetime

from pydantic import BaseModel


class TimelineEvent(BaseModel):
    event_id: str
    case_id: str
    event_type: str
    occurred_at: datetime
    description: str


