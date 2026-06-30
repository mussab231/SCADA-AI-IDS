import time
import numpy as np
import joblib
from collections import deque
from tensorflow.keras.models import load_model
from pymodbus.client import ModbusTcpClient
import requests
# ═════════════════════════════════════════════════════════════════════════════
# 1. SCADA & IDS Configuration
# ═════════════════════════════════════════════════════════════════════════════
PLC_IP        = '127.0.0.1'
PLC_PORT      = 502
MODEL_PATH    = 'scada_lstm_model.keras'
SCALER_PATH   = 'scada_scaler.pkl'
TIME_STEPS    = 40
SAMPLING_RATE = 0.5    # ثانية

# ── DETECTOR 1: LSTM — Tank0 Overflow ────────────────────────────────────────

ANOMALY_THRESHOLD = 0.04757   
TANK0_IDX         = 0         

# ── DETECTOR 2: Rule-Based — Mix_Ratio Rapid Oscillation ─────────────────────
MIX_RATIO_IDX          = 3     # Mix_Ratio هو الـ feature رقم 3 في raw_features
MIX_RATIO_LOW          = 100   # أي قيمة ≤ هذا = حالة "منخفضة" (≈ 0)
MIX_RATIO_HIGH         = 900   # أي قيمة ≥ هذا = حالة "مرتفعة" (≈ 1000)
MIX_RATIO_FLIP_WINDOW  = 15    # عدد العينات للنافذة الزمنية (15 × 0.5s = 7.5 ثانية)
MIX_RATIO_FLIP_THRESH  = 4     # عدد التقلبات 0↔1000 التي تعتبر هجوماً
#  ↑ مشتق من تحليل الداتا: يكشف الهجوم 9 نوافذ مع 0 false positives بالبيانات الطبيعية

# Feature names للـ logging
FEATURE_NAMES = [
    'Tank0_Level', 'Tank1_Level', 'Tank2_Level', 'Mix_Ratio',
    'Valve0_Fill', 'Valve0_Disch', 'Valve1_Fill', 'Valve1_Disch',
    'Valve2_Fill', 'Valve2_Disch'
]


# ═════════════════════════════════════════════════════════════════════════════
# 2. Mix_Ratio Oscillation Detector (Rule-Based)
# ═════════════════════════════════════════════════════════════════════════════
def count_extreme_flips(history, low_th, high_th):
    """
    يحسب عدد التقلبات بين الحالة المنخفضة (≤ low_th) والمرتفعة (≥ high_th).
    يتجاهل القيم الوسطية "mid" — فقط الانتقالات بين الطرفين تُحسب.

    مثال: [0, 500, 1000, 500, 0, 500, 1000] → 2 flips (0→1000، ثم 1000→0)
    """
    flips      = 0
    prev_state = None   # None | 'low' | 'high'

    for val in history:
        if val <= low_th:
            state = 'low'
        elif val >= high_th:
            state = 'high'
        else:
            state = 'mid'  

        # انتقال حقيقي بين طرفين مختلفين
        if (prev_state in ('low', 'high')
                and state in ('low', 'high')
                and state != prev_state):
            flips += 1

        # نحدّث prev_state فقط عند الوصول لطرف (لا للقيم الوسطية)
        if state in ('low', 'high'):
            prev_state = state

    return flips


# ═════════════════════════════════════════════════════════════════════════════
# 3. Main IDS Loop
# ═════════════════════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║      SCADA DUAL-MODE IDS ENGINE INITIALIZED     ║")
    print("║  [1] LSTM     → Tank0 Overflow Attack           ║")
    print("║  [2] RuleBased→ Mix_Ratio Oscillation Attack    ║")
    print("╚══════════════════════════════════════════════════╝")

    if ANOMALY_THRESHOLD == 0.00000:
        print("[CRITICAL] ANOMALY_THRESHOLD = 0. Run train_ids_model.py first and copy the value!")
        return

    # Load AI Model & Scaler
    try:
        print("[INFO] Loading LSTM Model and Scaler...")
        model  = load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("[INFO] AI brain loaded successfully.")
    except Exception as e:
        print(f"[CRITICAL] Failed to load AI components: {e}")
        return

    # Connect to Modbus
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    if not client.connect():
        print("[CRITICAL] Could not connect to SCADA network.")
        return

    print(f"[INFO] Connected to Modbus PLC at {PLC_IP}:{PLC_PORT}")
    print(f"[INFO] LSTM Threshold (Tank0)  : {ANOMALY_THRESHOLD:.5f}")
    print(f"[INFO] Mix_Ratio Flip Threshold: {MIX_RATIO_FLIP_THRESH} flips / "
          f"{MIX_RATIO_FLIP_WINDOW * SAMPLING_RATE:.1f}s window")
    print("─" * 55)

    # Buffers
    lstm_window     = deque(maxlen=TIME_STEPS)             # للـ LSTM
    mix_ratio_buf   = deque(maxlen=MIX_RATIO_FLIP_WINDOW)  # للـ rule-based

    try:
        while True:
            # ── قراءة Modbus ───────────────────────────────────────────────
            actuators = client.read_input_registers(address=0, count=6)
            sensors   = client.read_holding_registers(address=0, count=4)

            if actuators.isError() or sensors.isError():
                print("[WARNING] Packet loss. Retrying...")
                time.sleep(SAMPLING_RATE)
                continue

            raw_features = [
                sensors.registers[0],    # [0] Tank0_Level  ← مراقب بالـ LSTM
                sensors.registers[1],    # [1] Tank1_Level
                sensors.registers[2],    # [2] Tank2_Level
                sensors.registers[3],    # [3] Mix_Ratio    ← مراقب بالـ Rule
                actuators.registers[0],  # [4] Valve0_Fill
                actuators.registers[1],  # [5] Valve0_Disch
                actuators.registers[2],  # [6] Valve1_Fill
                actuators.registers[3],  # [7] Valve1_Disch
                actuators.registers[4],  # [8] Valve2_Fill
                actuators.registers[5],  # [9] Valve2_Disch
            ]

            mix_ratio_val = raw_features[MIX_RATIO_IDX]

            # ═══════════════════════════════════════════════════════════════
            # DETECTOR 2: Mix_Ratio Rapid Oscillation (Rule-Based)
            # يعمل فوراً — لا ينتظر امتلاء الـ LSTM buffer
            # ═══════════════════════════════════════════════════════════════
            mix_ratio_buf.append(mix_ratio_val)

            mix_attack = False
            flip_count = 0
            if len(mix_ratio_buf) == MIX_RATIO_FLIP_WINDOW:
                flip_count = count_extreme_flips(
                    mix_ratio_buf,
                    MIX_RATIO_LOW,
                    MIX_RATIO_HIGH
                )
                if flip_count >= MIX_RATIO_FLIP_THRESH:
                    mix_attack = True

            # ═══════════════════════════════════════════════════════════════
            # DETECTOR 1: LSTM — Tank0 Overflow
            # ═══════════════════════════════════════════════════════════════
            scaled_features = scaler.transform([raw_features])[0]
            lstm_window.append(scaled_features)

            lstm_attack  = False
            tank0_error  = 0.0

            if len(lstm_window) == TIME_STEPS:
                sequence   = np.array(lstm_window).reshape(1, TIME_STEPS, len(raw_features))
                prediction = model.predict(sequence, verbose=0)

                errors      = np.power(sequence - prediction, 2)  # (1, 40, 10)
                feature_mse = np.mean(errors[0], axis=0)          # (10,)
                tank0_error = feature_mse[TANK0_IDX]

                if tank0_error > ANOMALY_THRESHOLD:
                    lstm_attack = True

            # ═══════════════════════════════════════════════════════════════
            # OUTPUT & BACKEND COMMUNICATION
            # ═══════════════════════════════════════════════════════════════
            api_url = "http://localhost:5000/api/ids/log"
            payload = None

            if lstm_attack and mix_attack:
                msg = f"[🚨🚨 DUAL ATTACK] Tank0_Err={tank0_error:.5f} | MixRatio={mix_ratio_val} ({flip_count} flips)"
                print(msg)
                payload = {"status": "ATTACK", "max_error": float(tank0_error), "message": msg}

            elif lstm_attack:
                msg = f"[🚨 ATTACK-1 | TANK OVERFLOW] Tank0_Error={tank0_error:.5f} > {ANOMALY_THRESHOLD:.5f} | Tank0={raw_features[0]}"
                print(msg)
                payload = {"status": "ATTACK", "max_error": float(tank0_error), "message": msg}

            elif mix_attack:
                msg = f"[🚨 ATTACK-2 | MIX_RATIO OSCILLATION] Mix_Ratio flipped {flip_count}x | Current={mix_ratio_val}"
                print(msg)
                payload = {"status": "ATTACK", "max_error": float(flip_count), "message": msg}

            else:
                lstm_status = f"Tank0_Err={tank0_error:.5f}" if len(lstm_window) == TIME_STEPS else f"warming up ({len(lstm_window)}/{TIME_STEPS})"
                msg = f"[✅ NORMAL] {lstm_status} | Tank0={raw_features[0]}, MixRatio={mix_ratio_val}"
                print(msg)
                payload = {"status": "NORMAL", "max_error": float(tank0_error), "message": msg}

            # إرسال البيانات إلى خادم Node.js
            if payload:
                try:
                    requests.post(api_url, json=payload, timeout=0.5)
                except requests.exceptions.RequestException:
                    pass # تجاهل الخطأ مؤقتاً كي لا يتوقف السكريبت إذا كان السيرفر مغلقاً

            time.sleep(SAMPLING_RATE)
          

    except KeyboardInterrupt:
        print("\n[INFO] Real-time IDS manually terminated.")
    finally:
        client.close()


if __name__ == "__main__":
    main()