from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
from src.db.session import Base

class ThreatEvent(Base):
    __tablename__ = "threat_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source_ip = Column(String(50), index=True)
    endpoint = Column(String(255))
    payload = Column(Text, nullable=True)
    
    # AI Classifications
    threat_type = Column(String(50), index=True)  # e.g., SQLi, XSS, Normal
    severity = Column(String(20))                 # Low, Medium, High, Critical
    confidence_score = Column(Float)              # 0.0 to 1.0