from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as api_router

app = FastAPI(title="AngelusVigil AI Threat Detection")

# إعدادات الحماية للسماح للفرونت إند بالاتصال بالباك إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في بيئة الإنتاج نضع رابط الفرونت إند فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running smoothly!"}