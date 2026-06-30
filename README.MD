# SCADA-AI-IDS: Real-Time Cyber-Physical Intrusion Detection System

![SCADA Security](https://img.shields.io/badge/Security-ICS%2FSCADA-red)
![AI Engine](https://img.shields.io/badge/AI-LSTM%20Autoencoder-blue)
![Dashboard](https://img.shields.io/badge/Dashboard-MERN%20Stack-brightgreen)

## 📌 Project Overview

This project is an advanced, real-time Intrusion Detection System (IDS) engineered for Industrial Control Systems (ICS). Designed as a 5th-year Computer and Automatic Control Engineering graduation project, it bridges the gap between Operational Technology (OT) and Information Technology (IT) security.

The system monitors live Modbus TCP traffic from a SCADA environment, utilizing a dual-mode detection engine to identify physical anomalies and cyber-attacks (such as False Data Injection and Actuator Tampering) before physical damage occurs.

## 🏗️ System Architecture

The architecture is divided into three critical layers:

1. **OT Layer (The Plant):** \* **Factory I/O:** Simulates the physical water treatment plant (Tanks, Valves, Pumps).
   - **OpenPLC:** Executes Ladder Logic and serves as the Modbus TCP Server.
2. **AI / Security Layer (The Brain):**
   - **Python Sniffer:** Continuously intercepts Modbus registers holding sensor and actuator data.
   - **LSTM Autoencoder:** A Deep Learning model trained on the physical baseline of the plant to detect complex, multi-variable False Data Injection (FDI) attacks.
   - **Rule-Based Engine:** A deterministic algorithm to detect high-frequency mechanical tampering (Chattering/Oscillation attacks).
3. **IT / Monitoring Layer (The Command Center):**
   - **Node.js/Express Backend:** Ingests threat data via REST API.
   - **MongoDB Atlas:** Securely logs all incident records.
   - **React.js Frontend:** A secure, authenticated dashboard displaying real-time MSE (Mean Squared Error) charts via **WebSockets**.

## 🚀 Features

- **Zero-Latency Detection:** Processes Modbus traffic and evaluates physics violations in milliseconds.
- **Dual-Mode Engine:** Combines AI (Long Short-Term Memory networks) for unknown anomalies with Rule-based logic for specific mechanical abuse.
- **Live Incident Dashboard:** Real-time visual monitoring using `Recharts` and `Socket.io` without page reloads.
- **Hysteresis & Deadband Logic:** Physics-informed PLC programming to prevent false positives during normal plant operations.
- **Secure Architecture:** JWT-based authentication and isolated API routes.

## 🛠️ Technology Stack

- **Machine Learning:** TensorFlow, Keras, Scikit-learn, Numpy, Pandas, Joblib.
- **Industrial Protocols:** PyModbus (Modbus TCP).
- **Backend:** Node.js, Express, Mongoose, Socket.io, JWT, Bcrypt.
- **Frontend:** React, Vite, React-Router-Dom, Axios, Recharts.
- **Database:** MongoDB Atlas (Cloud).
- **Automation Control:** OpenPLC Editor, Factory I/O.

## ⚙️ Installation & Execution Guide

### 1. OT Environment Setup

1. Launch **Factory I/O** and open the designated plant scene.
2. Launch **OpenPLC**, load the compiled Ladder Logic (`.st` file), and start the Modbus server on `127.0.0.1:502`.
3. Connect Factory I/O to the OpenPLC Modbus driver.

### 2. Backend Setup

```bash
cd backend
npm install

```

Create a `.env` file in the `backend` directory:

```env
PORT=5000
MONGO_URI=mongodb+srv://<your_username>:<your_password>@cluster0.mongodb.net/scada_ids_db
JWT_SECRET=your_super_secret_key

```

Start the server:

```bash
node server.js

```

### 3. Frontend Setup (Command Center)

```bash
cd frontend
npm install
npm run dev

```

Navigate to `http://localhost:5173`. Use default admin credentials (`admin` / `admin123`) to access the dashboard.

### 4. AI Engine Execution

Open a new terminal and activate your Python environment:

```bash
cd machine_learning
pip install -r requirements.txt # (Ensure tensorflow, pymodbus, joblib, scikit-learn are installed)
python realtime_ids.py

```

_The system will now bridge the SCADA traffic to the AI model and broadcast alerts to the React Dashboard._

## 👨‍💻 Author

**Mussab Atif Asad** _Computerand Automatic Control Engineering_

---

_Disclaimer: This project was built for academic and research purposes to demonstrate cybersecurity vulnerabilities and mitigation strategies in industrial networks._

```

```
