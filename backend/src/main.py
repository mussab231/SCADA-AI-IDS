from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.db.session import engine, Base

# --- الحل المعماري: استدعاء الملف الذي يحتوي على جميع الجداول ---
from src.models import threat 

# --- بناء الجداول بناءً على الاستدعاء الشامل أعلاه ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vigil SOC WAF API")

# إعداد الـ CORS لكي يتصل الفرونت إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط المسارات
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Vigil WAF is running!"}