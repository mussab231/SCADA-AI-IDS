import urllib.request
import pandas as pd
import os


THREAT_FEEDS = {
    "SQL Injection": [
        "https://raw.githubusercontent.com/swisskyrepo/PayloadsAllTheThings/master/SQL%20Injection/Intruder/Auth_Bypass.txt"
    ],
    "XSS": [
       "https://raw.githubusercontent.com/danielmiessler/SecLists/a1f65aa54523a57f64a815f27e179a0c70fd3b44/Fuzzing/XSS/Polyglots/XSS-innerht-ml.txt"
    ]
}

CSV_PATH = "/app/data/master_dataset.csv"

def fetch_latest_threats():
    print(" بدء عملية الاستخبارات السيبرانية الذكية (Smart Intel)...")
    
    new_payloads = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for threat_type, urls in THREAT_FEEDS.items():
        for url in urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=10)
                data = response.read().decode('utf-8').split('\n')
                valid_payloads = [line.strip() for line in data if line.strip()]
                for payload in valid_payloads:
                    new_payloads.append({"Payload": payload, "Label": threat_type})
                print(f"✔️ نجح سحب {len(valid_payloads)} هجمة ({threat_type}).")
                break # نجحنا، لا داعي للرابط البديل
            except Exception as e:
                continue # جرب الرابط الذي يليه

    if not new_payloads:
        print("❌ فشل السحب بالكامل من جميع المصادر.")
        return

    df_new = pd.DataFrame(new_payloads)
    # إزالة التكرار من الهجمات "الجديدة" فقط!
    df_new.drop_duplicates(subset=['Payload'], inplace=True)
    
    if os.path.exists(CSV_PATH):
        df_old = pd.read_csv(CSV_PATH)
        # فلترة: خذ الهجمات الجديدة التي (لا توجد) في المستودع القديم
        new_unique = df_new[~df_new['Payload'].isin(df_old['Payload'])]
        
        if new_unique.empty:
            print("⚠️ جميع الهجمات المسحوبة موجودة لدينا مسبقاً.")
            return
            
        # دمج آمن دون المساس بأوزان المستودع القديم
        df_combined = pd.concat([df_old, new_unique], ignore_index=True)
        added_count = len(new_unique)
    else:
        df_combined = df_new
        added_count = len(df_new)

    df_combined.to_csv(CSV_PATH, index=False)
    print(f"🚀 اكتملت المهمة بسلام! تمت إضافة {added_count} هجمة سيبرانية فريدة بالموجب (+).")

if __name__ == "__main__":
    fetch_latest_threats()