import requests
import time
import random

# مسار البوابة الصناعية في الجدار الناري الخاص بك
URL = "http://localhost:8000/api/ics-check"

def send_modbus_pulse(fc, address, value, length):
    payload = {
        "function_code": fc,
        "address": address,
        "value": value,
        "length": length
    }
    try:
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            print(f"✅ مر بسلام   | FC:{fc}\tAddr:{address}\tVal:{value}\tLen:{length}")
        elif response.status_code == 403:
            print(f"💀 إعدام فوري | FC:{fc}\tAddr:{address}\tVal:{value}\tLen:{length} -> (AI BLOCKED)")
        else:
            print(f"⚠️ خطأ غير متوقع: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ السيرفر لا يرد! هل الجدار الناري يعمل؟")

print("🏭 بدء تشغيل محاكي المصنع...")
print("🎯 جاري حقن هجمات Zero-Day عشوائية...")
print("-" * 50)

# إرسال 50 نبضة متتالية (نبضة كل ثانية)
for i in range(50):
    time.sleep(1) # ننتظر ثانية لكي تستمتع بمشاهدة الرادار
    
    # احتمالية 70% أن يكون الترافيك طبيعي، و 30% هجوم مدمر
    if random.random() < 0.70:
        # ترافيك طبيعي (Normal)
        send_modbus_pulse(
            fc=random.choice([1, 2, 3, 4]), 
            address=random.randint(100, 500), 
            value=random.randint(0, 255), 
            length=random.randint(5, 12)
        )
    else:
        # هجوم Zero-Day (أوامر غريبة، أطوال مستحيلة، قيم حرجة)
        send_modbus_pulse(
            fc=random.choice([15, 16, 90, 255]), 
            address=random.randint(0, 10), 
            value=random.choice([0, 65280]), 
            length=random.randint(200, 500)
        )