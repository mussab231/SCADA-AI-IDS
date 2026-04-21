import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.utils import class_weight
import joblib
import os

CSV_PATH = "/app/data/master_dataset.csv"
MODEL_PATH = "/app/trained_models/lstm_model.h5"
TOKENIZER_PATH = "/app/trained_models/tokenizer.pkl"

MAX_WORDS = 5000
MAX_LEN = 150

print("⏳ جاري تحميل مستودع البيانات...")
df = pd.read_csv(CSV_PATH)
df.dropna(subset=['Payload', 'Label'], inplace=True)

# 1. التنظيف العنيف: إزالة كل التكرار الذي دمر الشبكة العصبية
df.drop_duplicates(subset=['Payload'], inplace=True)

print("🔬 جاري توليد بيانات ترافيك طبيعي متنوعة (Data Synthesis)...")
# 2. توليد آلاف العينات الطبيعية المتنوعة ديناميكياً بدلاً من تكرار سطر واحد
diverse_normals = []
for i in range(5000):
    # توليد إيميلات
    diverse_normals.append({"Payload": f"user_{i}.test@university.edu", "Label": "Normal"})
    # توليد مسارات بريئة
    diverse_normals.append({"Payload": f"https://site.com/api/v1/items?id={i}&sort=asc", "Label": "Normal"})
    # توليد JSON بريء يحتوي على فواصل (الحل الجذري لمشكلة O'Reilly)
    diverse_normals.append({"Payload": f"{{\"search\": \"Book_{i}'s Edition\", \"page\": {i%100}}}", "Label": "Normal"})
    # توليد بيانات تسجيل دخول عادية
    diverse_normals.append({"Payload": f"username=student{i}&password=Pass{i}Word!", "Label": "Normal"})

df_diverse = pd.DataFrame(diverse_normals)
df = pd.concat([df, df_diverse], ignore_index=True)

# خلط البيانات بقوة
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 3. التصنيف الثنائي (0 = طبيعي، 1 = هجوم)
df['Label_Num'] = np.where(df['Label'] == 'Normal', 0, 1)

X_raw = df['Payload'].astype(str).values
y = df['Label_Num'].values

print("🧠 جاري معالجة النصوص وبناء المترجم...")
tokenizer = Tokenizer(num_words=MAX_WORDS, char_level=True, lower=True)
tokenizer.fit_on_texts(X_raw)

os.makedirs("/app/trained_models", exist_ok=True)
joblib.dump(tokenizer, TOKENIZER_PATH)

X_seq = tokenizer.texts_to_sequences(X_raw)
X_padded = pad_sequences(X_seq, maxlen=MAX_LEN, padding='post')

# 4. حساب أوزان الكلاسات رياضياً لمنع الانحياز
weights = class_weight.compute_class_weight('balanced', classes=np.unique(y), y=y)
cw_dict = dict(enumerate(weights))

print("🏗️ جاري بناء شبكة LSTM العصبية...")
model = Sequential([
    Embedding(input_dim=MAX_WORDS, output_dim=32, input_length=MAX_LEN),
    LSTM(64, return_sequences=False),
    Dropout(0.5),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print("\n🔥 بدء التدريب العميق والنهائي...")
# لاحظ إضافة class_weight هنا لتوازن القوى
model.fit(X_padded, y, epochs=5, batch_size=128, validation_split=0.2, class_weight=cw_dict)

model.save(MODEL_PATH)
print(f"\n✅ تم تدريب وحفظ العقل العميق بنجاح في: {MODEL_PATH}")