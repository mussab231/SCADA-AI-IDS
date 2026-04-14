import os
import joblib

class ThreatAnalyzer:
    def __init__(self):
        # مسار النموذج داخل حاوية لينكس
        self.model_path = "/app/trained_models/rf_model.pkl"
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"✅ AI Model loaded successfully from {self.model_path}")
        else:
            print(f"⚠️ Warning: Model not found at {self.model_path}. AI features disabled.")

    def analyze(self, endpoint: str, payload: str) -> dict:
        """
        تحليل الترافيك باستخدام خوارزمية Random Forest المدربة.
        """
        payload_str = str(payload) if payload else ""
        
        # إذا لم يكن النموذج محملاً (تجنباً لانهيار الخادم)
        if self.model is None:
            return {"threat_type": "Unknown", "severity": "Low", "confidence_score": 0.0}

        # 1. التنبؤ بنوع الهجمة
        prediction = self.model.predict([payload_str])[0]
        
        # 2. حساب نسبة الثقة في القرار (Confidence Score)
        probabilities = self.model.predict_proba([payload_str])[0]
        confidence = max(probabilities)

        # 3. تحديد مستوى الخطورة ديناميكياً
        severity = "Low"
        if prediction in ["SQL Injection", "XSS"]:
            severity = "Critical" if confidence > 0.8 else "High"
        elif prediction != "Normal":
            severity = "Medium"

        return {
            "threat_type": str(prediction),
            "severity": severity,
            "confidence_score": round(float(confidence), 2)
        }

# إنشاء نسخة واحدة جاهزة للعمل
analyzer_instance = ThreatAnalyzer()