import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# استخدام "postgres" كقيمة افتراضية إجبارية لتجاوز فخ الـ localhost
POSTGRES_USER = os.getenv("POSTGRES_USER", "vigil_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "SuperSecretAdminPassword2026!")
POSTGRES_DB = os.getenv("POSTGRES_DB", "threat_db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")  # <-- السر هنا

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()