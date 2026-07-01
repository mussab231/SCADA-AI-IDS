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

ANOMALY_THRESHOLD = 0.04757   
TANK0_IDX         = 0         

MIX_RATIO_IDX          = 3     
MIX_RATIO_LOW          = 100   
MIX_RATIO_HIGH         = 900   
MIX_RATIO_FLIP_WINDOW  = 15    
MIX_RATIO_FLIP_THRESH  = 4     

def count_extreme_flips(history, low_th, high_th):
    flips      = 0
    prev_state = None   

    for val in history:
        if val <= low_th:
            state = 'low'
        elif val >= high_th:
            state = 'high'
        else:
            state = 'mid'  

        if (prev_state in ('low', 'high')
                and state in ('low', 'high')
                and state != prev_state):
            flips += 1

        if state in ('low', 'high'):
            prev_state = state

    return flips

def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║      SCADA DUAL-MODE IDS ENGINE INITIALIZED      ║")
    print("║  [1] LSTM     → Tank0 Overflow Attack            ║")
    print("║  [2] RuleBased→ Mix_Ratio Oscillation Attack     ║")
    print("╚══════════════════════════════════════════════════╝")

    if ANOMALY_THRESHOLD == 0.00000:
        print("[CRITICAL] ANOMALY_THRESHOLD = 0. Run train_ids_model.py first and copy the value!")
        return

    try:
        print("[INFO] Loading LSTM Model and Scaler...")
        model  = load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("[INFO] AI brain loaded successfully.")
    except Exception as e:
        print(f"[CRITICAL] Failed to load AI components: {e}")
        return

    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    if not client.connect():
        print("[CRITICAL] Could not connect to SCADA network.")
        return

    print(f"[INFO] Connected to Modbus PLC at {PLC_IP}:{PLC_PORT}")
    print(f"[INFO] LSTM Threshold (Tank0)  : {ANOMALY_THRESHOLD:.5f}")
    print(f"[INFO] Mix_Ratio Flip Threshold: {MIX_RATIO_FLIP_THRESH} flips / {MIX_RATIO_FLIP_WINDOW * SAMPLING_RATE:.1f}s window")
    print("─" * 55)

    lstm_window     = deque(maxlen=TIME_STEPS)             
    mix_ratio_buf   = deque(maxlen=MIX_RATIO_FLIP_WINDOW)  

    # المسار الصحيح للسيرفر
    api_url = "http://localhost:5000/api/scada/data"

    try:
        while True:
            actuators = client.read_input_registers(address=0, count=6)
            sensors   = client.read_holding_registers(address=0, count=4)

            if actuators.isError() or sensors.isError():
                print("[WARNING] Packet loss. Retrying...")
                time.sleep(SAMPLING_RATE)
                continue

            raw_features = [
                sensors.registers[0],    # [0] Tank0_Level
                sensors.registers[1],    # [1] Tank1_Level
                sensors.registers[2],    # [2] Tank2_Level
                sensors.registers[3],    # [3] Mix_Ratio
                actuators.registers[0],  # [4] Valve0_Fill
                actuators.registers[1],  # [5] Valve0_Disch
                actuators.registers[2],  # [6] Valve1_Fill
                actuators.registers[3],  # [7] Valve1_Disch
                actuators.registers[4],  # [8] Valve2_Fill
                actuators.registers[5],  # [9] Valve2_Disch
            ]

            mix_ratio_val = raw_features[MIX_RATIO_IDX]
            mix_ratio_buf.append(mix_ratio_val)

            mix_attack = False
            flip_count = 0
            if len(mix_ratio_buf) == MIX_RATIO_FLIP_WINDOW:
                flip_count = count_extreme_flips(mix_ratio_buf, MIX_RATIO_LOW, MIX_RATIO_HIGH)
                if flip_count >= MIX_RATIO_FLIP_THRESH:
                    mix_attack = True

            scaled_features = scaler.transform([raw_features])[0]
            lstm_window.append(scaled_features)

            lstm_attack  = False
            tank0_error  = 0.0

            if len(lstm_window) == TIME_STEPS:
                sequence   = np.array(lstm_window).reshape(1, TIME_STEPS, len(raw_features))
                prediction = model.predict(sequence, verbose=0)
                errors      = np.power(sequence - prediction, 2)  
                feature_mse = np.mean(errors[0], axis=0)          
                tank0_error = float(feature_mse[TANK0_IDX])

                if tank0_error > ANOMALY_THRESHOLD:
                    lstm_attack = True

            # بناء هيكل البيانات الصحيح المتوافق مع Node.js و React
            payload = {
                "status":       "NORMAL",
                "attackId":     None,
                "attackType":   None,
                "tank0":        int(raw_features[0]),
                "tank1":        int(raw_features[1]),
                "tank2":        int(raw_features[2]),
                "mixRatio":     int(raw_features[3]),
                "tank0_error":  tank0_error,
                "threshold":    float(ANOMALY_THRESHOLD),
                "fillValve0":   int(raw_features[4]),
                "dischValve0":  int(raw_features[5]),
                "fillValve1":   int(raw_features[6]),
                "dischValve1":  int(raw_features[7]),
                "fillValve2":   int(raw_features[8]),
                "dischValve2":  int(raw_features[9]),
            }

            if lstm_attack and mix_attack:
                payload["status"]     = "ATTACK-DUAL"
                payload["attackId"]   = 3
                payload["attackType"] = "OVERFLOW + OSCILLATION"
                print(f"[🚨🚨 DUAL ATTACK] Tank0_Err={tank0_error:.5f} | MixRatio={mix_ratio_val} ({flip_count} flips)")
            
            elif lstm_attack:
                payload["status"]     = "ATTACK-1"
                payload["attackId"]   = 1
                payload["attackType"] = "TANK OVERFLOW"
                print(f"[🚨 ATTACK-1] Tank0_Error={tank0_error:.5f} > {ANOMALY_THRESHOLD:.5f}")
            
            elif mix_attack:
                payload["status"]     = "ATTACK-2"
                payload["attackId"]   = 2
                payload["attackType"] = "MIX_RATIO OSCILLATION"
                print(f"[🚨 ATTACK-2] Mix_Ratio flipped {flip_count}x")
            
            else:
                lstm_status = f"Tank0_Err={tank0_error:.5f}" if len(lstm_window) == TIME_STEPS else f"warming up ({len(lstm_window)}/{TIME_STEPS})"
                print(f"[✅ NORMAL] {lstm_status} | Tank0={raw_features[0]}, MixRatio={mix_ratio_val}")

            # إرسال البيانات للـ Backend
            try:
                requests.post(api_url, json=payload, timeout=1.0)
            except requests.exceptions.RequestException as e:
                print(f"[⚠️ WARNING] Could not reach backend at {api_url}: {e}")

            time.sleep(SAMPLING_RATE)
          
    except KeyboardInterrupt:
        print("\n[INFO] Real-time IDS manually terminated.")
    finally:
        client.close()

if __name__ == "__main__":
    main()