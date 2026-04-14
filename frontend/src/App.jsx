import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [threats, setThreats] = useState([]);

  useEffect(() => {
    // 1. جلب السجل التاريخي (مرة واحدة فقط)
    const fetchHistory = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/threats/");
        const data = await response.json();
        setThreats(data);
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };
    fetchHistory();

    // 2. فتح قناة WebSocket للاستماع اللحظي
    const ws = new WebSocket("ws://localhost:8000/api/ws/threats");

    ws.onopen = () => {
      console.log("🟢 WebSocket Connected: Listening for threats...");
    };

    ws.onmessage = (event) => {
      const newThreat = JSON.parse(event.data);
      console.log("🚨 New Threat Detected!", newThreat);
      // إضافة الهجمة الجديدة إلى أعلى القائمة دون إعادة تحميل البيانات القديمة
      setThreats((prevThreats) => [newThreat, ...prevThreats]);
    };

    ws.onclose = () => {
      console.log("🔴 WebSocket Disconnected");
    };

    // تنظيف الاتصال إذا تم إغلاق المكون
    return () => {
      if (ws.readyState === 1) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="dashboard">
      <header className="header">
        <h1>🛡️ AngelusVigil | AI Threat Radar</h1>
        <div className="status-badge">Live WebSocket Active</div>
      </header>

      <div className="threat-grid">
        {threats.map((threat) => (
          <div
            key={threat.id}
            className={`threat-card ${threat.severity.toLowerCase()}`}
          >
            <div className="card-header">
              <h3>{threat.threat_type}</h3>
              <span className={`badge ${threat.severity.toLowerCase()}`}>
                {threat.severity}
              </span>
            </div>
            <div className="card-body">
              <p>
                <strong>IP:</strong> {threat.source_ip}
              </p>
              <p>
                <strong>Target:</strong> {threat.endpoint}
              </p>
              <p>
                <strong>Payload:</strong>{" "}
                <span className="code">{threat.payload || "N/A"}</span>
              </p>
              <p>
                <strong>AI Confidence:</strong>{" "}
                {(threat.confidence_score * 100).toFixed(1)}%
              </p>
              <p className="time">
                {new Date(threat.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
