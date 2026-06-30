import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, RepeatVector, TimeDistributed, Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib

# Configuration
NORMAL_DATA_PATH = 'datasets/scada_normal_baseline.csv'
ATTACK_DATA_PATH = 'datasets/scada_attack_data.csv'
TIME_STEPS = 40

# Feature index mapping (must match realtime_ids.py order exactly)
FEATURE_NAMES = [
    'Tank0_Level',   # index 0 ← الخزان الرئيسي (المستهدف بالمراقبة)
    'Tank1_Level',   # index 1
    'Tank2_Level',   # index 2
    'Mix_Ratio',     # index 3
    'Valve0_Fill',   # index 4
    'Valve0_Disch',  # index 5
    'Valve1_Fill',   # index 6
    'Valve1_Disch',  # index 7
    'Valve2_Fill',   # index 8
    'Valve2_Disch',  # index 9
]
TANK0_IDX = 0  # ← نراقب هذا الـ feature فقط في الـ runtime

def load_and_preprocess_data(filepath, scaler=None, is_training=False):
    """Loads CSV, drops Timestamp, scales data, and creates time-series sequences."""
    print(f"[INFO] Loading data from: {filepath}")
    df = pd.read_csv(filepath)

    if 'Timestamp' in df.columns:
        df = df.drop(columns=['Timestamp'])

    data_values = df.values

    if is_training:
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data_values)
    else:
        scaled_data = scaler.transform(data_values)

    sequences = []
    for i in range(len(scaled_data) - TIME_STEPS):
        sequences.append(scaled_data[i:(i + TIME_STEPS)])

    return np.array(sequences), scaler


def build_lstm_autoencoder(sequence_length, num_features):
    """Builds the LSTM Autoencoder architecture."""
    model = Sequential([
        LSTM(32, activation='relu', input_shape=(sequence_length, num_features), return_sequences=True),
        LSTM(16, activation='relu', return_sequences=False),
        Dropout(0.2),
        RepeatVector(sequence_length),
        LSTM(16, activation='relu', return_sequences=True),
        LSTM(32, activation='relu', return_sequences=True),
        TimeDistributed(Dense(num_features))
    ])
    model.compile(optimizer='adam', loss='mse')
    return model


def compute_feature_mse(X, predictions):
    """
    حساب MSE لكل feature على حدة (نفس طريقة الـ runtime بالضبط).
    Returns shape: (n_samples, n_features)
    """
    errors = np.power(X - predictions, 2)          # (n_samples, TIME_STEPS, n_features)
    return np.mean(errors, axis=1)                  # (n_samples, n_features)


def main():
    print("==================================================")
    print("     SCADA LSTM AUTOENCODER TRAINING INITIATED    ")
    print("==================================================")

    # 1. Load data
    X_normal, scaler = load_and_preprocess_data(NORMAL_DATA_PATH, is_training=True)
    print(f"[INFO] Normal sequences shape: {X_normal.shape}")

    X_attack, _ = load_and_preprocess_data(ATTACK_DATA_PATH, scaler=scaler, is_training=False)
    print(f"[INFO] Attack sequences shape: {X_attack.shape}")

    # 2. Build & Train
    num_features = X_normal.shape[2]
    model = build_lstm_autoencoder(TIME_STEPS, num_features)
    model.summary()

    print("\n[INFO] Starting model training on NORMAL data only...")
    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    model.fit(
        X_normal, X_normal,
        epochs=30,
        batch_size=32,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=1
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 3. حساب الـ Threshold بنفس الطريقة المستخدمة في الـ runtime
    #    (feature-wise MSE → نركز على Tank0 فقط)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[INFO] Calculating per-feature thresholds on Normal Data...")
    normal_predictions = model.predict(X_normal)

    # (n_samples, n_features) → MSE لكل feature في كل sequence
    normal_feature_mse = compute_feature_mse(X_normal, normal_predictions)

    # Threshold للـ Tank0 فقط (99th percentile من بيانات طبيعية)
    TANK0_THRESHOLD = np.percentile(normal_feature_mse[:, TANK0_IDX], 99)

    # للمراجعة: thresholds كل الـ features
    all_thresholds = np.percentile(normal_feature_mse, 99, axis=0)

    print("\n" + "="*55)
    print("  *** COPY THIS INTO realtime_ids.py ***")
    print(f"  ANOMALY_THRESHOLD = {TANK0_THRESHOLD:.5f}   ← Tank0 only")
    print("="*55)
    print("\n[INFO] Per-feature thresholds (for reference):")
    for name, thr in zip(FEATURE_NAMES, all_thresholds):
        marker = " ← مراقب" if name == 'Tank0_Level' else ""
        print(f"  {name:<15}: {thr:.5f}{marker}")

    # 4. تقييم على بيانات الهجوم
    print("\n[INFO] Evaluating on Attack Data...")
    attack_predictions = model.predict(X_attack)
    attack_feature_mse = compute_feature_mse(X_attack, attack_predictions)

    normal_tank0_mse = normal_feature_mse[:, TANK0_IDX]
    attack_tank0_mse = attack_feature_mse[:, TANK0_IDX]

    # حساب الـ Detection Rate
    detected = (attack_tank0_mse > TANK0_THRESHOLD).sum()
    total    = len(attack_tank0_mse)
    print(f"\n[RESULT] Tank0 Detection Rate: {detected}/{total} = {100*detected/total:.1f}%")
    print(f"[RESULT] Normal False Positive Rate: "
          f"{(normal_tank0_mse > TANK0_THRESHOLD).sum()}/{len(normal_tank0_mse)} = "
          f"{100*(normal_tank0_mse > TANK0_THRESHOLD).mean():.2f}%")

    # 5. حفظ الموديل والـ scaler
    model.save('scada_lstm_model.keras')
    print("\n[INFO] Model saved: scada_lstm_model.keras")
    joblib.dump(scaler, 'scada_scaler.pkl')
    print("[INFO] Scaler saved: scada_scaler.pkl")

    # 6. رسمة Tank0 فقط (واضحة ومركزة)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # يسار: Tank0 MSE distribution
    axes[0].hist(normal_tank0_mse, bins=50, alpha=0.7, color='blue',  label='Normal (Tank0)')
    axes[0].hist(attack_tank0_mse, bins=50, alpha=0.7, color='red',   label='Attack (Tank0)')
    axes[0].axvline(TANK0_THRESHOLD, color='black', linestyle='--', linewidth=2,
                    label=f'Tank0 Threshold ({TANK0_THRESHOLD:.5f})')
    axes[0].set_title('Tank0 Reconstruction Error — Normal vs Attack')
    axes[0].set_xlabel('MSE (Tank0 Feature Only)')
    axes[0].set_ylabel('Number of Samples')
    axes[0].legend()
    axes[0].grid(True)

    # يمين: كل الـ features thresholds
    axes[1].barh(FEATURE_NAMES, all_thresholds, color=['red' if i == TANK0_IDX else 'steelblue'
                                                         for i in range(len(FEATURE_NAMES))])
    axes[1].set_title('Per-Feature Anomaly Thresholds (99th Percentile)')
    axes[1].set_xlabel('MSE Threshold')
    axes[1].axvline(TANK0_THRESHOLD, color='red', linestyle='--', linewidth=1, alpha=0.5)
    axes[1].grid(True, axis='x')

    plt.tight_layout()
    plt.savefig('threshold_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[INFO] Chart saved: threshold_analysis.png")


if __name__ == "__main__":
    main()