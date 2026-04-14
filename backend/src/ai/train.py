import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import os

# 1. تحديد مسار البيانات المدمجة الحقيقية
csv_path = "/app/data/master_dataset.csv"

if not os.path.exists(csv_path):
    print(f"❌ خطأ قاتل: ملف {csv_path} غير موجود!")
    exit(1)

print("⏳ جاري تحميل البيانات من مستودع CSV الضخم...")
df = pd.read_csv(csv_path)

# تنظيف البيانات من أي قيم فارغة قد تدمر التدريب
df.dropna(subset=['Payload', 'Label'], inplace=True)

print(f"🧠 جاري تدريب محرك الذكاء الاصطناعي على {len(df)} سجل ترافيك... (قد يستغرق هذا بعض الوقت)")

# 2. بناء خط الأنابيب (Pipeline)
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=(1, 3))), 
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)) # n_jobs=-1 يعتصر كل طاقة المعالج لديك
])

# 3. التدريب الفعلي
pipeline.fit(df['Payload'], df['Label'])

# 4. حفظ النموذج المحدث
os.makedirs("/app/trained_models", exist_ok=True)
model_path = "/app/trained_models/rf_model.pkl"
joblib.dump(pipeline, model_path)

print(f"✅ تم التدريب بنجاح! تم استبدال العقل القديم بالعقل الجديد في: {model_path}")