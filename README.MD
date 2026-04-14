# 🛡️ AngelusVigil | AI-Powered Web Application Firewall (WAF)

An advanced, microservices-based AI Threat Detection System designed to protect web applications and industrial control interfaces from cyber-attacks in real-time.

## 🏗️ Architecture Overview

The system is built on a containerized microservices architecture, utilizing Machine Learning for anomaly detection and WebSockets for real-time telemetry.

- **Frontend:** React.js dashboard with active WebSocket listeners for real-time threat visualization.
- **Backend:** FastAPI (Python) asynchronous server handling traffic routing and ML model serving.
- **Security Layer:** Redis-based rate limiting algorithm to mitigate DDoS and brute-force attempts.
- **Database:** PostgreSQL for immutable logging of threat events, managed via SQLAlchemy and Alembic.
- **AI Engine:** Random Forest Classifier & TF-IDF Vectorizer trained on 56,000+ real-world payloads to detect SQL Injection, XSS, and Path Traversal with high confidence.
- **Infrastructure:** Fully dockerized environment using Docker Compose.

## ✨ Core Features

1. **AI Pattern Recognition:** Generalizes attack patterns mathematically rather than relying on static regex rules (High confidence scoring).
2. **Real-Time Broadcasting:** Full-duplex WebSocket connections instantly push threats to the radar dashboard.
3. **Active Rate Limiting:** Drops malicious traffic dynamically (HTTP 429) before it reaches the AI inference engine, saving CPU cycles.
4. **Stress-Tested:** Proven to handle simulated burst attacks and continuous traffic smoothly.

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose installed on your machine.

### Installation & Run

1. Clone the repository:

   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME

   ```

2. Boot the microservices architecture:
   docker compose up -d --build

3. Access the interfaces:

Live Dashboard: http://localhost:5173

API Swagger UI: http://localhost:8000/docs

🧠 ML Data Pipeline
Note: Datasets and trained .pkl models are excluded from this repository. To retrain the engine locally, place your raw .csv payloads in backend/data/ and execute the ETL pipeline script merge_data.py, followed by the training script train.py.
