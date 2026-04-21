from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from pydantic import BaseModel

from src.db.session import get_db
from src.models.threat import TrafficLog, TrafficStatus, SecurityRule, RuleType, TargetType
from src.schemas.threat import RuleCreate
from src.ai.analyzer import analyzer_instance
from src.db.limiter import rate_limiter

router = APIRouter()

class LoginCredentials(BaseModel):
    username: str
    password: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/threats")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/rules/")
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    # تخزين القيم كنصوص عادية لضمان عدم انهيار Postgres
    new_rule = SecurityRule(
        rule_type=rule.rule_type,
        target_type=rule.target_type,
        target_value=rule.target_value
    )
    db.add(new_rule)
    db.commit()
    return {"status": "success", "message": "Security rule applied successfully."}

@router.post("/secure-login")
async def secure_login(credentials: LoginCredentials, request: Request, db: Session = Depends(get_db)):
    payload_str = f"{credentials.username} {credentials.password}"
    client_ip = request.client.host if request.client else "Unknown"
    
    current_status = None
    current_reason = ""
    threat_type_detected = "Normal"
    confidence = 1.0

    rules = db.query(SecurityRule).all()
    # مقارنة النصوص (.value)
    blacklists = [r.target_value for r in rules if r.rule_type == RuleType.BLACKLIST.value]
    whitelists = [r.target_value for r in rules if r.rule_type == RuleType.WHITELIST.value]

    if client_ip in blacklists or payload_str in blacklists:
        current_status = TrafficStatus.BLOCKED
        current_reason = "Manual Blacklist"
        threat_type_detected = "Known Threat"
        confidence = 1.0

    elif client_ip in whitelists or payload_str in whitelists:
        current_status = TrafficStatus.MANUAL_BYPASS
        current_reason = "Manual Whitelist Bypass"
        threat_type_detected = "Normal"
        confidence = 1.0

    else:
        analysis = analyzer_instance.analyze(endpoint="/api/secure-login", payload=payload_str)
        threat_type_detected = analysis["threat_type"]
        confidence = analysis["confidence_score"]
        
        if threat_type_detected != "Normal":
            current_status = TrafficStatus.BLOCKED
            current_reason = f"AI Blocked: {threat_type_detected}"
        else:
            current_status = TrafficStatus.ALLOWED
            current_reason = "AI Cleared"

    # حفظ السجل بالاعتماد على النصوص
    db_log = TrafficLog(
        source_ip=client_ip,
        endpoint="/api/secure-login",
        payload=payload_str,
        threat_type=threat_type_detected,
        severity="High" if current_status == TrafficStatus.BLOCKED else "Low",
        confidence_score=confidence,
        status=current_status.value, 
        reason=current_reason
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    log_data = {
        "id": db_log.id,
        "timestamp": db_log.timestamp.isoformat(),
        "source_ip": db_log.source_ip,
        "status": db_log.status, 
        "threat_type": db_log.threat_type,
        "reason": db_log.reason,
        "payload": db_log.payload
    }
    await manager.broadcast(json.dumps(log_data))

    if current_status == TrafficStatus.BLOCKED:
        raise HTTPException(status_code=403, detail=current_reason)

    return {"status": "success", "message": "Login processed safely.", "waf_status": current_status.value}

@router.get("/logs/")
def get_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs