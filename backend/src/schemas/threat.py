from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrafficLogResponse(BaseModel):
    id: int
    timestamp: datetime
    source_ip: str
    endpoint: str
    payload: str
    threat_type: str
    severity: str
    confidence_score: float
    status: str
    reason: str

    class Config:
        from_attributes = True

class RuleCreate(BaseModel):
    rule_type: str    # "blacklist" أو "whitelist"
    target_type: str  # "ip" أو "payload"
    target_value: str        