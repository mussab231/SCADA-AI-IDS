import pandas as pd
import os

data_dir = "/app/data"

print("⏳ جاري قراءة الملفات الخام ومعالجة مشاكل الترميز (Encoding)...")

# 1. دالة القراءة الآمنة لتخطي أخطاء الترميز والملفات المفقودة
def safe_read_csv(file_path):
    if not os.path.exists(file_path):
        print(f"⚠️ تنويه: الملف {file_path} غير موجود. سيتم تخطيه برمجياً.")
        return None
    try:
        return pd.read_csv(file_path, on_bad_lines='skip', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return pd.read_csv(file_path, on_bad_lines='skip', encoding='utf-16')
        except UnicodeDecodeError:
            return pd.read_csv(file_path, on_bad_lines='skip', encoding='latin1')

# 2. قراءة الملفات من المجلد
df_sqli1 = safe_read_csv(f"{data_dir}/sqli.csv")
df_sqli2 = safe_read_csv(f"{data_dir}/sqliv2.csv")
df_sqli3 = safe_read_csv(f"{data_dir}/SQLiV3.csv")

# مستقبلاً: بمجرد أن تحمل ملف xss.csv وتضعه في المجلد، سيتعرف عليه السكربت تلقائياً
df_xss = safe_read_csv(f"{data_dir}/xss.csv") 
df_pt = safe_read_csv(f"{data_dir}/path_traversal.csv")


# 3. دالة هندسية لمعالجة وتصنيف كل إطار بيانات (DataFrame) على حدة قبل الدمج
def process_dataframe(df, attack_name):
    if df is None or df.empty:
        return pd.DataFrame() # إرجاع جدول فارغ إذا كان الملف غير موجود
    
    # نأخذ أول عمودين فقط لتوحيد الهيكل
    temp_df = df.iloc[:, :2].copy()
    temp_df.columns = ['Payload', 'NumericLabel']
    
    # تحويل القيم الرقمية إلى تصنيف الهجمة الممرر للدالة
    def map_label(val):
        val = str(val).strip()
        if val in ['1', '1.0']: 
            return attack_name # نضع اسم الهجمة الصحيح (مثلاً XSS أو SQL Injection)
        elif val in ['0', '0.0']: 
            return 'Normal'
        return 'Drop' # رمي القيم التالفة
        
    temp_df['Label'] = temp_df['NumericLabel'].apply(map_label)
    temp_df = temp_df[temp_df['Label'] != 'Drop']
    temp_df.drop(columns=['NumericLabel'], inplace=True)
    
    return temp_df

print("🧹 جاري تنظيف ومعالجة وتصنيف البيانات لكل نوع هجمة...")

processed_dfs = []

# معالجة بيانات SQLi (تمتلك 3 ملفات)
for df in [df_sqli1, df_sqli2, df_sqli3]:
    processed_dfs.append(process_dataframe(df, 'SQL Injection'))

# معالجة بيانات الهجمات الأخرى (ستعمل تلقائياً إذا وجدت الملفات)
processed_dfs.append(process_dataframe(df_xss, 'XSS'))
processed_dfs.append(process_dataframe(df_pt, 'Path Traversal'))

# 4. دمج كل البيانات المعالجة والنظيفة في مستودع واحد
master_df = pd.concat(processed_dfs, ignore_index=True)

# 5. الفلترة النهائية (إزالة التكرارات والقيم الفارغة)
master_df.dropna(inplace=True)
master_df.drop_duplicates(inplace=True)

# 6. الحفظ
master_path = f"{data_dir}/master_dataset.csv"
master_df.to_csv(master_path, index=False, encoding='utf-8')

print(f"✅ تمت هندسة البيانات بنجاح!")
print(f"📊 الحجم النهائي للبيانات الشاملة: {len(master_df)} سطر.")
print(f"📁 تم حفظ مستودع البيانات في: {master_path}")