require("dotenv").config();
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const mongoose = require("mongoose");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcrypt");
const cors = require("cors");

// ─── App & HTTP server ────────────────────────────────────────────────────────
const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

app.use(cors());
app.use(express.json());

// ─── MongoDB Schemas ──────────────────────────────────────────────────────────
const incidentSchema = new mongoose.Schema({
  timestamp: { type: Date, default: Date.now },
  status: { type: String, required: true },
  attackId: Number,
  attackType: String,
  tank0: Number,
  tank1: Number,
  tank2: Number,
  mixRatio: Number,
  tank0_error: Number,
  threshold: Number,
  fillValve0: Number,
  dischValve0: Number,
  fillValve1: Number,
  dischValve1: Number,
  fillValve2: Number,
  dischValve2: Number,
  acknowledged: { type: Boolean, default: false },
});

const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  passwordHash: { type: String, required: true },
  role: { type: String, default: "admin" },
});

const Incident = mongoose.model("Incident", incidentSchema);
const User = mongoose.model("User", userSchema);

// ─── MongoDB connect ──────────────────────────────────────────────────────────
mongoose
  .connect(process.env.MONGO_URI)
  .then(async () => {
    console.log("[DB] MongoDB Atlas connected");
    await seedAdmin();
  })
  .catch((err) => {
    console.error("[DB] Connection error:", err);
    process.exit(1);
  });

// إصلاح دالة إنشاء الـ Admin لجلب البيانات من .env
async function seedAdmin() {
  const adminUser = process.env.ADMIN_USERNAME;
  const adminPass = process.env.ADMIN_PASSWORD;

  // إذا كانت المتغيرات مفقودة، أوقف السيرفر فوراً
  if (!adminUser || !adminPass) {
    console.error(
      "[FATAL] ADMIN_USERNAME or ADMIN_PASSWORD missing in .env file!",
    );
    process.exit(1);
  }

  const exists = await User.findOne({ username: adminUser });
  if (!exists) {
    const hash = await bcrypt.hash(adminPass, 12);
    await User.create({
      username: adminUser,
      passwordHash: hash,
      role: "admin",
    });
    console.log(`[DB] Admin user created (${adminUser}) from .env variables.`);
  } else {
    console.log(`[DB] Admin user (${adminUser}) already exists.`);
  }
}

// ─── Auth middleware ──────────────────────────────────────────────────────────
function requireAuth(req, res, next) {
  const header = req.headers.authorization;
  if (!header || !header.startsWith("Bearer "))
    return res.status(401).json({ error: "Missing token" });

  try {
    req.user = jwt.verify(header.split(" ")[1], process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: "Invalid or expired token" });
  }
}

// ─── Routes ───────────────────────────────────────────────────────────────────

// POST /api/auth/login
app.post("/api/auth/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password)
    return res.status(400).json({ error: "Username and password required" });

  const user = await User.findOne({ username });
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign(
    { username: user.username, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: "8h" },
  );

  res.json({ token, role: user.role, username: user.username });
});

// POST /api/scada/data
app.post("/api/scada/data", async (req, res) => {
  const data = req.body;

  if (data.status && data.status !== "NORMAL") {
    try {
      await Incident.create({
        status: data.status,
        attackId: data.attackId,
        attackType: data.attackType,
        tank0: data.tank0,
        tank1: data.tank1,
        tank2: data.tank2,
        mixRatio: data.mixRatio,
        tank0_error: data.tank0_error,
        threshold: data.threshold,
        fillValve0: data.fillValve0,
        dischValve0: data.dischValve0,
        fillValve1: data.fillValve1,
        dischValve1: data.dischValve1,
        fillValve2: data.fillValve2,
        dischValve2: data.dischValve2,
      });
    } catch (err) {
      console.error("[DB] Incident save error:", err.message);
    }
  }

  // بث البيانات الحية فور وصولها
  io.emit("scada_update", {
    ...data,
    serverTime: new Date().toISOString(),
  });

  res.json({ ok: true });
});

// GET /api/incidents
app.get("/api/incidents", requireAuth, async (req, res) => {
  try {
    const incidents = await Incident.find()
      .sort({ timestamp: -1 })
      .limit(100)
      .lean();
    res.json(incidents);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── Socket.io ────────────────────────────────────────────────────────────────
io.on("connection", (socket) => {
  console.log("[WS] Dashboard connected:", socket.id);
  socket.on("disconnect", () =>
    console.log("[WS] Dashboard disconnected:", socket.id),
  );
});

// ─── Start ────────────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 5000;
server.listen(PORT, () =>
  console.log(`[SRV] SCADA IDS backend running on http://localhost:${PORT}`),
);
