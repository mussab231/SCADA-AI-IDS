import React, { useState, useEffect } from "react";

const ThreatRadar = () => {
  const [logs, setLogs] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("Connecting...");

  useEffect(() => {
    // 1. جلب التاريخ القديم (History)
    fetch("http://localhost:8000/api/logs/")
      .then((res) => res.json())
      .then((data) => setLogs(data))
      .catch((err) => console.error("Error fetching history:", err));

    // 2. فتح قناة الاتصال اللحظي (WebSockets)
    const ws = new WebSocket("ws://localhost:8000/api/ws/threats");

    ws.onopen = () => setConnectionStatus("Live WebSocket Active");
    ws.onclose = () => setConnectionStatus("Disconnected");

    ws.onmessage = (event) => {
      const newLog = JSON.parse(event.data);
      // إضافة السجل الجديد في أعلى القائمة
      setLogs((prevLogs) => [newLog, ...prevLogs]);
    };

    return () => ws.close();
  }, []);

  // 3. دالة إرسال الأوامر للباك إند (أزرار التحكم)
  const applySecurityRule = async (ruleType, targetType, targetValue) => {
    try {
      const response = await fetch("http://localhost:8000/api/rules/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          rule_type: ruleType,
          target_type: targetType,
          target_value: targetValue,
        }),
      });

      if (response.ok) {
        alert(`تم تطبيق القاعدة بنجاح: ${ruleType} على ${targetValue}`);
      } else {
        alert("فشل تطبيق القاعدة! تأكد أنها غير مكررة.");
      }
    } catch (error) {
      console.error("Error applying rule:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      {/* شريط العنوان والحالة */}
      <div className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold tracking-wider text-cyan-400">
          🛡️ VIGIL SOC | <span className="text-white">COMMAND CENTER</span>
        </h1>
        <div
          className={`px-4 py-2 rounded-full border ${connectionStatus.includes("Live") ? "border-cyan-500 text-cyan-400" : "border-red-500 text-red-400"}`}
        >
          {connectionStatus}
        </div>
      </div>

      {/* شبكة البطاقات (الرادار) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {logs.map((log, index) => {
          // تحديد ألوان البطاقة بناءً على الحالة
          const isBlocked = log.status === "blocked";
          const isBypass = log.status === "manual_bypass";

          const borderColor = isBlocked
            ? "border-red-500"
            : isBypass
              ? "border-yellow-500"
              : "border-green-500";
          const statusBg = isBlocked
            ? "bg-red-900 text-red-200"
            : isBypass
              ? "bg-yellow-900 text-yellow-200"
              : "bg-green-900 text-green-200";

          return (
            <div
              key={log.id || index}
              className={`bg-gray-800 rounded-lg p-5 border-l-4 ${borderColor} shadow-lg flex flex-col justify-between`}
            >
              {/* رأس البطاقة */}
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold">
                  {log.threat_type || "Unknown"}
                </h3>
                <span className={`text-xs px-2 py-1 rounded ${statusBg}`}>
                  {log.status.toUpperCase()}
                </span>
              </div>

              {/* تفاصيل الترافيك */}
              <div className="space-y-2 text-sm text-gray-300 mb-6">
                <p>
                  <span className="font-semibold text-gray-500">IP:</span>{" "}
                  {log.source_ip}
                </p>
                <p>
                  <span className="font-semibold text-gray-500">Target:</span>{" "}
                  {log.endpoint}
                </p>
                <div className="bg-gray-900 p-2 rounded text-xs font-mono break-all text-pink-400">
                  {log.payload}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  <span className="font-semibold">Reason:</span> {log.reason}
                </p>
                <p className="text-xs text-gray-500 text-right mt-2">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </p>
              </div>

              {/* أزرار التحكم اليدوية (SOC Actions) */}
              <div className="flex gap-2 mt-auto border-t border-gray-700 pt-4">
                {/* زر الإعدام (حظر الـ IP) */}
                <button
                  onClick={() =>
                    applySecurityRule("blacklist", "ip", log.source_ip)
                  }
                  className="flex-1 bg-red-950 hover:bg-red-900 text-red-400 text-xs py-2 rounded transition-colors border border-red-800"
                >
                  Block IP
                </button>

                {/* زر العفو (استثناء الـ Payload) */}
                <button
                  onClick={() =>
                    applySecurityRule("whitelist", "payload", log.payload)
                  }
                  className="flex-1 bg-green-950 hover:bg-green-900 text-green-400 text-xs py-2 rounded transition-colors border border-green-800"
                >
                  Whitelist Payload
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ThreatRadar;
