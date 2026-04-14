from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# هذا الكلاس يمثل شكل البيانات التي سنستقبلها من الخارج
class ThreatCreate(BaseModel):
    source_ip: str
    endpoint: str
    payload: Optional[str] = None
    threat_type: str = "Unknown"
    severity: str = "Low"
    confidence_score: float = 0.0

# هذا الكلاس يمثل شكل البيانات التي سنرد بها (تتضمن الـ ID والوقت)
class ThreatResponse(ThreatCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True