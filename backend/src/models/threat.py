from sqlalchemy import Column, Integer, String, DateTime, Float
import datetime
from src.db.session import Base
import enum

class TrafficStatus(str, enum.Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    MANUAL_BYPASS = "manual_bypass"

class RuleType(str, enum.Enum):
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"

class TargetType(str, enum.Enum):
    IP = "ip"
    PAYLOAD = "payload"

class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_ip = Column(String)
    endpoint = Column(String)
    payload = Column(String)
    
    threat_type = Column(String)
    severity = Column(String) 
    confidence_score = Column(Float)
    
    # تحويل العمود إلى نص عادي لتخزين القيم بأمان
    status = Column(String, default=TrafficStatus.ALLOWED.value)
    reason = Column(String)

class SecurityRule(Base):
    __tablename__ = "security_rules"

    id = Column(Integer, primary_key=True, index=True)
    # تحويل الأعمدة إلى نصوص عادية
    rule_type = Column(String)
    target_type = Column(String)
    target_value = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)