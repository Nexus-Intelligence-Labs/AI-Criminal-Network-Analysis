from datetime import datetime

from pydantic import BaseModel


class Case(BaseModel):
    case_id: str
    title: str
    status: str = "OPEN"
    created_at: datetime
