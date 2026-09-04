from datetime import datetime

from pydantic import BaseModel


class Alert(BaseModel):
    alert_id: str
    title: str
    severity: str
    created_at: datetime
    status: str = "OPEN"


