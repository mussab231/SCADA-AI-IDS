import os
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

class ThreatAnalyzer:
    def __init__(self):
        # كتم تحذيرات TensorFlow المزعجة في الـ Terminal لتنظيف السجلات
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

        print("🧠 جاري إيقاظ العقول الأمنية (Web & ICS)...")

        # ==========================================
        # 1. مسارات عقل الويب (LSTM - SQLi)
        # ==========================================
        self.web_model_path = "/app/trained_models/lstm_model.h5"
        self.web_tokenizer_path = "/app/trained_models/tokenizer.pkl"
        self.max_len = 150
        
        self.web_model = None
        self.web_tokenizer = None

        # ==========================================
        # 2. مسارات العقل الصناعي (Autoencoder - Zero-Day)
        # ==========================================
        self.ics_model_path = "/app/trained_models/zero_day_autoencoder.h5"
        self.ics_scaler_path = "/app/trained_models/zero_day_scaler.pkl"
        self.ics_threshold_path = "/app/trained_models/zero_day_threshold.txt"
        
        self.ics_model = None
        self.ics_scaler = None
        self.ics_threshold = 0.0

        # تشغيل دالة التحميل المزدوج
        self._load_brains()

    def _load_brains(self):
        """تحميل الشبكات العصبية إلى الذاكرة مرة واحدة فقط عند إقلاع السيرفر"""
        
        # --- تحميل عقل الويب ---
        print("🌐 جاري تحميل عقل الويب (LSTM)...")
        if os.path.exists(self.web_model_path) and os.path.exists(self.web_tokenizer_path):
            try:
                self.web_model = load_model(self.web_model_path)
                self.web_tokenizer = joblib.load(self.web_tokenizer_path)
                print("✅ تم ربط عقل الويب بنجاح!")
            except Exception as e:
                print(f"❌ خطأ أثناء تحميل عقل الويب: {e}")
        else:
            print("⚠️ تحذير: ملفات عقل الويب غير موجودة. مسار الويب سيعمل بشكل أعمى.")

        # --- تحميل العقل الصناعي ---
        print("🏭 جاري تحميل العقل الصناعي (Zero-Day Autoencoder)...")
        if os.path.exists(self.ics_model_path) and os.path.exists(self.ics_scaler_path):
            try:
                self.ics_model = load_model(self.ics_model_path)
                self.ics_scaler = joblib.load(self.ics_scaler_path)
                with open(self.ics_threshold_path, "r") as f:
                    self.ics_threshold = float(f.read().strip())
                print(f"✅ تم تحميل العقل الصناعي! خط الدفاع: {self.ics_threshold}")
            except Exception as e:
                print(f"❌ خطأ أثناء تحميل العقل الصناعي: {e}")
        else:
            print("⚠️ تحذير: ملفات العقل الصناعي غير موجودة. النظام سيعمل بشكل أعمى.")

    # ==========================================
    # دالة تحليل الويب (الاستنتاج اللحظي لـ JSON/SQLi)
    # ==========================================
    def analyze(self, endpoint: str, payload: str) -> dict:
        if not self.web_model or not self.web_tokenizer:
            return {"threat_type": "AI Engine Offline", "severity": "Critical", "confidence_score": 1.0}

        # المعالجة اللغوية والاستنتاج
        sequence = self.web_tokenizer.texts_to_sequences([payload])
        padded_sequence = pad_sequences(sequence, maxlen=self.max_len, padding='post')
        prediction_score = self.web_model.predict(padded_sequence, verbose=0)[0][0]

        if prediction_score > 0.5:
            threat_type = "SQL Injection"
            severity = "High" if prediction_score > 0.8 else "Medium"
            confidence = prediction_score
        else:
            threat_type = "Normal"
            severity = "Low"
            confidence = 1.0 - prediction_score 

        return {
            "threat_type": threat_type,
            "severity": severity,
            "confidence_score": float(confidence)
        }

    # ==========================================
    # دالة التحليل الصناعي (Zero-Day Detector لـ Modbus)
    # ==========================================
    def analyze_modbus(self, fc, address, value, length):
        if not self.ics_model or not self.ics_scaler:
            return {"threat_type": "AI Engine Offline", "severity": "Critical", "confidence_score": 1.0, "mse": 0.0}
        
        # ضغط البيانات وتجهيزها
        input_data = np.array([[fc, address, value, length]])
        scaled_data = self.ics_scaler.transform(input_data)
        
        # محاولة إعادة البناء وقياس الخطأ
        reconstructed = self.ics_model.predict(scaled_data, verbose=0)
        mse = np.mean(np.power(scaled_data - reconstructed, 2))
        
        # اتخاذ قرار الإعدام الصناعي
        if mse > self.ics_threshold:
            confidence = min(1.0, mse / (self.ics_threshold * 2))
            return {
                "threat_type": "Zero-Day Anomaly (SCADA)",
                "severity": "Critical",
                "confidence_score": float(confidence),
                "mse": float(mse)
            }
        else:
            return {
                "threat_type": "Normal",
                "severity": "Low",
                "confidence_score": 1.0,
                "mse": float(mse)
            }

# إنشاء نسخة واحدة (Singleton) ليستخدمها السيرفر
analyzer_instance = ThreatAnalyzer()