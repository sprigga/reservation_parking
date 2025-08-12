import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .api import router
from .database import Base, engine, SessionLocal
from . import models
from .auth import get_password_hash

app = FastAPI(title="Reservation Parking API")

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup and ensure default admin
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    with SessionLocal() as db:
        exists = db.execute(select(models.User).where(models.User.username == admin_username)).scalar_one_or_none()
        if not exists:
            u = models.User(
                username=admin_username,
                password_hash=get_password_hash(admin_password),
                is_admin=True,
                is_active=True,
            )
            db.add(u)
            db.commit()

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
