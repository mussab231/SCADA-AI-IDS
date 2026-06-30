require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

app.use(cors());
app.use(express.json());

// ==========================================
// 1. MongoDB Schemas & Models (هنا يتم تعريف User يا مهندس!)
// ==========================================
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, default: "Security_Admin" },
});
const User = mongoose.model("User", userSchema);

const alertSchema = new mongoose.Schema({
  timestamp: { type: Date, default: Date.now },
  status: { type: String, required: true }, // 'NORMAL' or 'ATTACK'
  max_error: { type: Number, required: true },
  message: { type: String, required: true },
});
const Alert = mongoose.model("Alert", alertSchema);

// ==========================================
// 2. Database Connection & Admin Init
// ==========================================
mongoose
  .connect(process.env.MONGO_URI)
  .then(async () => {
    console.log("[INFO] Connected to MongoDB: scada_ids_db");

    // قراءة بيانات الأدمن من ملف البيئة المخفي
    const adminUser = process.env.ADMIN_USERNAME;
    const adminPass = process.env.ADMIN_PASSWORD;

    if (adminUser && adminPass) {
      const adminExists = await User.findOne({ username: adminUser });
      if (!adminExists) {
        const hashedPassword = await bcrypt.hash(adminPass, 10);
        await User.create({ username: adminUser, password: hashedPassword });
        console.log(
          `[CRITICAL] Security Admin [${adminUser}] created from .env configuration.`,
        );
      }
    } else {
      console.log(
        "[WARNING] ADMIN_USERNAME or ADMIN_PASSWORD missing in .env. No default admin created.",
      );
    }
  })
  .catch((err) => console.error("[ERROR] MongoDB Connection Failed:", err));
// ==========================================
// 3. API Routes
// ==========================================

app.post("/api/auth/login", async (req, res) => {
  const { username, password } = req.body;
  try {
    const user = await User.findOne({ username });
    if (!user)
      return res
        .status(401)
        .json({ error: "Access Denied. Invalid credentials." });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch)
      return res
        .status(401)
        .json({ error: "Access Denied. Invalid credentials." });

    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "12h" },
    );
    res.json({ token });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/ids/log", async (req, res) => {
  try {
    const { status, max_error, message } = req.body;
    const newAlert = new Alert({ status, max_error, message });
    await newAlert.save();

    io.emit("new_scada_log", newAlert);

    res.status(200).json({ success: true, message: "Log registered" });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ==========================================
// 4. Server Execution
// ==========================================
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`[INFO] SCADA Backend Engine running on port ${PORT}`);
});
