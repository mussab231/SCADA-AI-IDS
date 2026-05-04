import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import random

MODEL_PATH = "/app/trained_models/zero_day_autoencoder.h5"
SCALER_PATH = "/app/trained_models/zero_day_scaler.pkl"
THRESHOLD_PATH = "/app/trained_models/zero_day_threshold.txt"

print("🏭 جاري توليد بيانات الترافيك الصناعي (الطبيعي فقط)...")

# 1. توليد ترافيك "طبيعي" نقي 100% ليتعلمه النظام (لا يوجد أي هجوم هنا)
normal_data = []
for _ in range(25000):
    # بروتوكول Modbus/TCP الآمن
    fc = random.choice([1, 2, 3, 4])       # أوامر القراءة فقط (آمنة)
    address = random.randint(100, 500)     # عناوين عامة
    value = random.randint(0, 255)         # قيم روتينية
    length = random.randint(5, 12)         # أطوال الحزم الطبيعية
    normal_data.append([fc, address, value, length])

df_normal = pd.DataFrame(normal_data, columns=['Function_Code', 'Address', 'Value', 'Length'])
X_normal = df_normal.values

print("⚖️ جاري تسوية الأرقام (Scaling)...")
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_normal)

os.makedirs("/app/trained_models", exist_ok=True)
joblib.dump(scaler, SCALER_PATH)

print("🏗️ جاري بناء شبكة Autoencoder (العقل المضاد للمجهول)...")
input_dim = X_scaled.shape[1]

# الطبقة المدخلة
input_layer = Input(shape=(input_dim,))

# المشفر (Encoder) - يضغط البيانات ليفهم جوهرها المعماري
encoded = Dense(8, activation='relu')(input_layer)
encoded = Dense(4, activation='relu')(encoded)

# النواة المركزية (Latent Space) - هنا يتم تخزين "بصمة" الترافيك الطبيعي
latent = Dense(2, activation='relu')(encoded)

# فك التشفير (Decoder) - يحاول إعادة بناء البيانات من البصمة
decoded = Dense(4, activation='relu')(latent)
decoded = Dense(8, activation='relu')(decoded)
output_layer = Dense(input_dim, activation='sigmoid')(decoded)

autoencoder = Model(inputs=input_layer, outputs=output_layer)
autoencoder.compile(optimizer='adam', loss='mse')

print("\n🔥 بدء تدريب العقل على 'الوضع الطبيعي' فقط...")
# لاحظ الإعجاز الهندسي هنا: المدخلات والمخرجات هي نفس البيانات (X_scaled, X_scaled)
autoencoder.fit(X_scaled, X_scaled, epochs=15, batch_size=64, validation_split=0.2)

autoencoder.save(MODEL_PATH)

print("\n📐 جاري حساب عتبة الإعدام (Reconstruction Error Threshold)...")
# نجعل الشبكة تختبر نفسها على البيانات الطبيعية لمعرفة متوسط خطأها الطبيعي
predictions = autoencoder.predict(X_scaled)
mse = np.mean(np.power(X_scaled - predictions, 2), axis=1)

# نحدد العتبة عند 99.9% (أي شيء يتجاوز خطأ 99.9% من الترافيك الطبيعي هو هجوم مؤكد)
threshold = np.percentile(mse, 99.9) 

with open(THRESHOLD_PATH, "w") as f:
    f.write(str(threshold))

print(f"\n✅ تم الحفظ! أي ترافيك صناعي يتجاوز نسبة خطأ [{threshold:.6f}] سيتم سحقه كـ Zero-Day.")