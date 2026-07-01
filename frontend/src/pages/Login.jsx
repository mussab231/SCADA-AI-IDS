import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = "http://localhost:5000";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError("Both fields are required.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Authentication failed.");
        setLoading(false);
        return;
      }

      localStorage.setItem("scada_token", data.token);
      navigate("/dashboard");
    } catch {
      setError(
        "Cannot reach server. Make sure the backend is running on port 5000.",
      );
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a0e1a",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Courier New', monospace",
      }}
    >
      {/* Background grid lines for industrial feel */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "linear-gradient(rgba(6,182,212,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(6,182,212,0.03) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div
        style={{
          background: "#111827",
          border: "1px solid #1e2d40",
          borderRadius: 8,
          padding: "36px 40px",
          width: "100%",
          maxWidth: 360,
          position: "relative",
        }}
      >
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div
            style={{
              color: "#06b6d4",
              fontSize: 12,
              letterSpacing: 3,
              marginBottom: 6,
            }}
          >
            SCADA IDS AUTH
          </div>
          <div style={{ color: "#1e3a5f", fontSize: 9, letterSpacing: 1 }}>
            INDUSTRIAL CONTROL SYSTEM — SECURE ACCESS
          </div>
          <div
            style={{
              width: 40,
              height: 2,
              background:
                "linear-gradient(90deg, transparent, #06b6d4, transparent)",
              margin: "12px auto 0",
            }}
          />
        </div>

        <form onSubmit={handleLogin}>
          {/* Username */}
          <div style={{ marginBottom: 14 }}>
            <label
              style={{
                color: "#64748b",
                fontSize: 9,
                letterSpacing: 1,
                display: "block",
                marginBottom: 5,
              }}
            >
              OPERATOR ID
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                setError("");
              }}
              placeholder="admin"
              autoComplete="username"
              style={{
                width: "100%",
                boxSizing: "border-box",
                background: "#0d1b2e",
                border: "1px solid #1e2d40",
                borderRadius: 4,
                padding: "9px 12px",
                color: "#e2e8f0",
                fontSize: 12,
                fontFamily: "'Courier New', monospace",
                outline: "none",
              }}
              onFocus={(e) => (e.target.style.borderColor = "#06b6d4")}
              onBlur={(e) => (e.target.style.borderColor = "#1e2d40")}
            />
          </div>

          {/* Password */}
          <div style={{ marginBottom: 20 }}>
            <label
              style={{
                color: "#64748b",
                fontSize: 9,
                letterSpacing: 1,
                display: "block",
                marginBottom: 5,
              }}
            >
              ACCESS CODE
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError("");
              }}
              placeholder="••••••••"
              autoComplete="current-password"
              style={{
                width: "100%",
                boxSizing: "border-box",
                background: "#0d1b2e",
                border: "1px solid #1e2d40",
                borderRadius: 4,
                padding: "9px 12px",
                color: "#e2e8f0",
                fontSize: 12,
                fontFamily: "'Courier New', monospace",
                outline: "none",
              }}
              onFocus={(e) => (e.target.style.borderColor = "#06b6d4")}
              onBlur={(e) => (e.target.style.borderColor = "#1e2d40")}
            />
          </div>

          {/* Error message */}
          {error && (
            <div
              style={{
                background: "rgba(239,68,68,0.1)",
                border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: 4,
                padding: "7px 12px",
                marginBottom: 14,
                color: "#ef4444",
                fontSize: 10,
              }}
            >
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              background: loading ? "#1e3a5f" : "#0e4d7a",
              border: "1px solid #06b6d4",
              borderRadius: 4,
              color: loading ? "#64748b" : "#06b6d4",
              padding: "10px",
              fontSize: 11,
              letterSpacing: 2,
              cursor: loading ? "not-allowed" : "pointer",
              fontFamily: "'Courier New', monospace",
              fontWeight: 700,
              transition: "background 0.2s",
            }}
          >
            {loading ? "AUTHENTICATING..." : "SYSTEM LOGIN"}
          </button>
        </form>

        {/* Footer */}
        <div
          style={{
            textAlign: "center",
            marginTop: 20,
            color: "#1e3a5f",
            fontSize: 9,
          }}
        >
          UNAUTHORIZED ACCESS IS PROHIBITED
        </div>
      </div>
    </div>
  );
}
