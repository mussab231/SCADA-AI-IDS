import requests
import random
import time

# مسار الـ API الخاص بنا
URL = "http://localhost:8000/api/threats/"

# قائمة هجمات حقيقية ومتنوعة
base_payloads = [
    # SQL Injection
    "admin' OR 1=1 --", 
    "1; DROP TABLE users", 
    "' UNION SELECT username, password FROM admins --",
    "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)",
    
    # XSS (Cross-Site Scripting)
    "<script>alert('Hacked')</script>", 
    "<img src=x onerror=alert(document.cookie)>", 
    "\"><svg/onload=confirm(1)>",
    "javascript:eval('var a=document.createElement(\\'script\\');...')",

    # Path Traversal
    "../../../../etc/shadow",
    "%2e%2e%2f%2e%2e%2fwindows%2fsystem32",
    
    # الترافيك الطبيعي (للاختبار المزدوج)
    "mosab_2026", 
    "search=laptop",
    "john.doe@email.com"
]

# تكرار القائمة وخلطها عشوائياً لتوليد 100 هجمة
attack_arsenal = (base_payloads * 10)[:100]
random.shuffle(attack_arsenal)

print("🚀 بدء هجوم المحاكاة (Stress Test) على السيرفر...")
print("-" * 50)

success_count = 0
blocked_count = 0

for i, payload in enumerate(attack_arsenal):
    # نولد IP وهمي ليظهر في قاعدة البيانات (لكن الـ IP الحقيقي للشبكة سيبقى نفسه)
    fake_ip = f"192.168.1.{random.randint(1, 255)}"
    
    data = {
        "source_ip": fake_ip,
        "endpoint": random.choice(["/login", "/search", "/upload", "/api/data"]),
        "payload": payload
    }

    try:
        # إرسال الهجمة
        response = requests.post(URL, json=data)
        
        if response.status_code == 200:
            print(f"[{i+1:02d}] 🔴 تم المرور للذكاء الاصطناعي -> {payload[:30]}...")
            success_count += 1
        elif response.status_code == 429:
            print(f"[{i+1:02d}] 🛡️ محظور من Redis (429) -> {payload[:30]}...")
            blocked_count += 1
        else:
            print(f"[{i+1:02d}] ⚠️ خطأ سيرفر: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"[{i+1:02d}] ❌ فشل الاتصال بالسيرفر! هل Docker يعمل؟")
        break
    
    # تأخير بسيط جداً (عُشر ثانية) لمحاكاة هجوم واقعي
    time.sleep(0.1)

print("-" * 50)
print(f"🏁 انتهى الهجوم. مرت {success_count} هجمات، وتم حظر {blocked_count} هجمات.")