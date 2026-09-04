from datetime import datetime

from pydantic import BaseModel


class Evidence(BaseModel):
    evidence_id: str
    case_id: str
    evidence_type: str
    source: str
    collected_at: datetime
