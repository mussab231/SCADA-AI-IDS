from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import json
from src.db.session import get_db
from src.models.threat import ThreatEvent
from src.schemas.threat import ThreatCreate, ThreatResponse
from src.ai.analyzer import analyzer_instance
from src.db.limiter import rate_limiter

router = APIRouter()

# --- 1. مدير قنوات WebSocket ---
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

# --- 2. مسار WebSocket (القناة المفتوحة) ---
@router.websocket("/ws/threats")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # نبقي القناة مفتوحة وننتظر أي رسالة (حتى لو فارغة) كنبض (Ping)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- 3. مسار استقبال الهجمات (محمي + يبث فوراً) ---
@router.post("/threats/", response_model=ThreatResponse, dependencies=[Depends(rate_limiter)])
async def create_threat(threat: ThreatCreate, db: Session = Depends(get_db)):
    analysis_result = analyzer_instance.analyze(threat.endpoint, threat.payload)
    
    db_threat = ThreatEvent(
        source_ip=threat.source_ip,
        endpoint=threat.endpoint,
        payload=threat.payload,
        threat_type=analysis_result["threat_type"],
        severity=analysis_result["severity"],
        confidence_score=analysis_result["confidence_score"]
    )
    
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)

    # تجهيز رسالة البث
    threat_data = {
        "id": db_threat.id,
        "source_ip": db_threat.source_ip,
        "endpoint": db_threat.endpoint,
        "payload": db_threat.payload,
        "threat_type": db_threat.threat_type,
        "severity": db_threat.severity,
        "confidence_score": db_threat.confidence_score,
        "timestamp": db_threat.timestamp.isoformat()
    }
    
    # دفع البيانات عبر القناة لكل المتصلين لحظياً
    await manager.broadcast(json.dumps(threat_data))
    
    return db_threat

# --- 4. مسار جلب السجل التاريخي ---
@router.get("/threats/", response_model=List[ThreatResponse])
def get_threats(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    threats = db.query(ThreatEvent).order_by(ThreatEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return threats