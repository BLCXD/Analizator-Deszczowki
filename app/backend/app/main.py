from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Analizator Deszczówki API", version="0.1.0")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8080")
allow_origins = [origin.strip() for origin in cors_origins.split(",")] if "," in cors_origins else [cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import auth, devices, measurements, push, admin
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["devices"])
app.include_router(measurements.router, prefix="/api/v1/measurements", tags=["measurements"])
app.include_router(push.router, prefix="/api/v1/push", tags=["push"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.on_event("startup")
def configure_admin_account():
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    if not email:
        return
    from app.db.session import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    try:
        db.query(User).filter(User.is_admin.is_(True), User.email != email).update({User.is_admin: False})
        user = db.query(User).filter(User.email == email).first()
        if user and not user.is_admin:
            user.is_admin = True
            db.commit()
    finally:
        db.close()

@app.get("/health")
async def health_check():
    from app.db.session import engine
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "ok"}
