FROM python:3.11-slim

WORKDIR /app

# تثبيت الحزم الأساسية لنظام لينكس (مهمة جداً لتعمل مكتبة قاعدة البيانات psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# الأمر الافتراضي لتشغيل الخادم (سيتم تجاوزه من ملف الـ compose للـ Hot Reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]