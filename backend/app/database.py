import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Example: mysql+pymysql://user:password@localhost:3306/reservation_parking
    "mysql+pymysql://root:password@localhost:3306/reservation_parking",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
