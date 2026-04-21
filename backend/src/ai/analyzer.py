import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
import numpy as np

class ThreatAnalyzer:
    def __init__(self):
        self.model_path = "/app/trained_models/lstm_model.h5"
        self.tokenizer_path = "/app/trained_models/tokenizer.pkl"
        self.max_len = 150 # يجب أن يطابق ما استخدمناه في التدريب
        
        self.model = None
        self.tokenizer = None
        
        self._load_brain()

    def _load_brain(self):
        """تحميل الشبكة العصبية والمترجم مرة واحدة فقط عند إقلاع السيرفر"""
        print("🧠 جاري تحميل شبكة LSTM العصبية العميقة إلى الذاكرة...")
        if os.path.exists(self.model_path) and os.path.exists(self.tokenizer_path):
            # كتم تحذيرات TensorFlow المزعجة في الـ Terminal
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
            self.model = load_model(self.model_path)
            self.tokenizer = joblib.load(self.tokenizer_path)
            print("✅ تم ربط العقل العميق بنجاح!")
        else:
            print("⚠️ تحذير: ملفات العقل العميق غير موجودة. النظام سيعمل بشكل أعمى.")

    def analyze(self, endpoint: str, payload: str) -> dict:
        """دالة الاستنتاج اللحظي"""
        # إذا لم يكن العقل محملاً، نمرر الطلب كـ Normal لتجنب انهيار السيرفر
        if not self.model or not self.tokenizer:
            return {
                "threat_type": "Unknown",
                "severity": "Low",
                "confidence_score": 0.0
            }

        # 1. المعالجة اللغوية (Tokenization & Padding)
        sequence = self.tokenizer.texts_to_sequences([payload])
        padded_sequence = pad_sequences(sequence, maxlen=self.max_len, padding='post')

        # 2. الاستنتاج العصبي (Inference)
        prediction_score = self.model.predict(padded_sequence, verbose=0)[0][0]

        # 3. اتخاذ القرار المعماري
        # بما أننا استخدمنا Sigmoid، النتيجة بين 0.0 و 1.0
        # أقرب للـ 1 يعني SQLi، أقرب للـ 0 يعني Normal
        if prediction_score > 0.5:
            threat_type = "SQL Injection"
            severity = "High" if prediction_score > 0.8 else "Medium"
            confidence = prediction_score
        else:
            threat_type = "Normal"
            severity = "Low"
            # إذا كان قريباً من الصفر، فالثقة بأنه طبيعي هي (1 - النتيجة)
            confidence = 1.0 - prediction_score 

        return {
            "threat_type": threat_type,
            "severity": severity,
            "confidence_score": float(confidence)
        }

# إنشاء نسخة واحدة (Singleton) ليستخدمها السيرفر
analyzer_instance = ThreatAnalyzer()