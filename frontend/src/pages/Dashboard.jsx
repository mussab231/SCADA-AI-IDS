import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

// الاتصال المباشر بالسيرفر عبر WebSockets
const socket = io("http://localhost:5000");

export default function Dashboard() {
  const navigate = useNavigate();
  const [dataStream, setDataStream] = useState([]);
  const [systemStatus, setSystemStatus] = useState("WAITING FOR DATA...");
  const [isUnderAttack, setIsUnderAttack] = useState(false);

  useEffect(() => {
    // التنصت على قناة الإنذارات القادمة من السيرفر
    socket.on("new_scada_log", (log) => {
      const newPoint = {
        time: new Date(log.timestamp).toLocaleTimeString(),
        error: parseFloat(log.max_error).toFixed(4),
        status: log.status,
        message: log.message,
      };

      // تحديث الحالة العامة
      if (log.status === "ATTACK") {
        setSystemStatus("🚨 CYBER ATTACK DETECTED 🚨");
        setIsUnderAttack(true);
      } else {
        setSystemStatus("✅ SYSTEM SECURE");
        setIsUnderAttack(false);
      }

      // إضافة النقطة الجديدة للمخطط (والاحتفاظ بآخر 30 قراءة فقط لمنع انهيار المتصفح)
      setDataStream((prev) => {
        const updatedStream = [...prev, newPoint];
        return updatedStream.length > 30
          ? updatedStream.slice(1)
          : updatedStream;
      });
    });

    // تنظيف الاتصال عند الخروج
    return () => socket.off("new_scada_log");
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("scada_token");
    navigate("/");
  };

  return (
    <div
      style={{
        backgroundColor: "#0a0a0a",
        minHeight: "100vh",
        color: "white",
        fontFamily: "monospace",
        padding: "2rem",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #333",
          paddingBottom: "1rem",
          marginBottom: "2rem",
        }}
      >
        <div>
          <h1 style={{ margin: 0, color: "#00ffcc", letterSpacing: "2px" }}>
            SCADA IDS COMMAND CENTER
          </h1>
          <p style={{ margin: 0, color: "#888", marginTop: "0.5rem" }}>
            Industrial Control System Real-Time Monitoring
          </p>
        </div>
        <button
          onClick={handleLogout}
          style={{
            padding: "0.6rem 1.5rem",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontWeight: "bold",
          }}
        >
          SYSTEM LOGOUT
        </button>
      </div>

      {/* Top Bar Status */}
      <div
        style={{
          padding: "1.5rem",
          backgroundColor: isUnderAttack ? "#4a0000" : "#001f14",
          border: `2px solid ${isUnderAttack ? "#ff4d4d" : "#00ffcc"}`,
          borderRadius: "8px",
          textAlign: "center",
          marginBottom: "2rem",
          transition: "all 0.3s ease",
        }}
      >
        <h2
          style={{
            margin: 0,
            color: isUnderAttack ? "#ff4d4d" : "#00ffcc",
            fontSize: "2rem",
          }}
        >
          {systemStatus}
        </h2>
        {dataStream.length > 0 && (
          <p style={{ color: "#ccc", marginTop: "0.5rem", fontSize: "1.2rem" }}>
            {dataStream[dataStream.length - 1].message}
          </p>
        )}
      </div>

      {/* Live Chart Section */}
      <div
        style={{
          backgroundColor: "#111",
          padding: "1rem",
          borderRadius: "8px",
          border: "1px solid #333",
          height: "400px",
        }}
      >
        <h3 style={{ margin: "0 0 1rem 0", color: "#aaa" }}>
          Live Anomaly Detection (MSE Stream)
        </h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dataStream}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis dataKey="time" stroke="#888" />
            <YAxis stroke="#888" domain={["auto", "auto"]} />
            <Tooltip
              contentStyle={{ backgroundColor: "#222", borderColor: "#444" }}
            />
            <Line
              type="monotone"
              dataKey="error"
              stroke={isUnderAttack ? "#ff4d4d" : "#00ffcc"}
              strokeWidth={3}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
