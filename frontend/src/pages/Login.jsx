import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // إرسال الطلب إلى سيرفر Node.js
      const res = await axios.post("http://localhost:5000/api/auth/login", {
        username,
        password,
      });

      // حفظ مفتاح الدخول وتوجيه المستخدم
      localStorage.setItem("scada_token", res.data.token);
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      setError("Access Denied. Invalid Credentials.");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#121212",
        color: "#00ffcc",
        fontFamily: "monospace",
      }}
    >
      <form
        onSubmit={handleLogin}
        style={{
          padding: "2rem",
          backgroundColor: "#1e1e1e",
          borderRadius: "8px",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
          width: "300px",
          border: "1px solid #333",
        }}
      >
        <h2 style={{ textAlign: "center", margin: 0 }}>SCADA IDS AUTH</h2>
        {error && (
          <div
            style={{
              color: "#ff4d4d",
              fontSize: "0.9rem",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}

        <input
          type="text"
          placeholder="Admin Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={{
            padding: "0.8rem",
            backgroundColor: "#2d2d2d",
            border: "1px solid #444",
            color: "white",
            outline: "none",
          }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{
            padding: "0.8rem",
            backgroundColor: "#2d2d2d",
            border: "1px solid #444",
            color: "white",
            outline: "none",
          }}
        />

        <button
          type="submit"
          style={{
            padding: "0.8rem",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            cursor: "pointer",
            fontWeight: "bold",
            letterSpacing: "1px",
          }}
        >
          SYSTEM LOGIN
        </button>
      </form>
    </div>
  );
}
