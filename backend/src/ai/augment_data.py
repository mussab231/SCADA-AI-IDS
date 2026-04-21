import pandas as pd

CSV_PATH = "/app/data/master_dataset.csv"

# 1. تجهيز الترافيك الطبيعي "القاسي" (Hard Negatives)
tricky_normals = [
    {"Payload": "{\"search\": \"O'Reilly books\", \"page\": 1}", "Label": "Normal"},
    {"Payload": "Hi, I'm John O'Connor. I love SQL databases.", "Label": "Normal"},
    {"Payload": "Please SELECT your favorite color from the dropdown list.", "Label": "Normal"},
    {"Payload": "{\"name\": \"D'Angelo\", \"comment\": \"drop the bass\"}", "Label": "Normal"},
    {"Payload": "It's a beautiful day to learn UNION and SELECT in university.", "Label": "Normal"},
    {"Payload": "user_id=105&name=McDonald's&order=1", "Label": "Normal"},
    {"Payload": "{\"query\": \"How to prevent SQL Injection in PHP?\"}", "Label": "Normal"}
]

# نكرر هذه العينات 1500 مرة لكي نعطيها وزناً ملحوظاً في قاعدة البيانات
tricky_normals = tricky_normals * 1500

print("⏳ جاري قراءة مستودع البيانات القديم...")
df_old = pd.read_csv(CSV_PATH)
df_new = pd.DataFrame(tricky_normals)

# 2. دمج البيانات
df_combined = pd.concat([df_old, df_new], ignore_index=True)

# 3. الضربة السحرية: خلط البيانات (Shuffling)
# هذا سيمنع الشبكة العصبية من الحفظ الأعمى وسيرفع دقة الـ (val_accuracy)
print("🔀 جاري خلط ملايين السطور لمنع الحفظ الأعمى (Overfitting)...")
df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

# 4. حفظ البيانات الجديدة
df_combined.to_csv(CSV_PATH, index=False)
print(f"✅ تمت إضافة {len(df_new)} عينة ترافيك طبيعي مخادع.")
print("✅ تم خلط البيانات وحفظ المستودع بنجاح! النظام جاهز لإعادة التدريب.")