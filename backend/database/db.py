# backend/database/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/studyflow_db")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("✅ PostgreSQL ডাটাবেস ব্যবহার করা হচ্ছে")
else:
    SQLITE_URL = "sqlite:///./studyflow.db"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    print("✅ SQLite ডাটাবেস ব্যবহার করা হচ্ছে (ডেভেলপমেন্ট)")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency - ডাটাবেস সেশন পাওয়ার জন্য
    ব্যবহার: db: Session = Depends(get_db)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_session() -> Session:
    """সিঙ্গেল সেশন পাওয়ার জন্য (ব্যাকএন্ডে ব্যবহার)"""
    return SessionLocal()

def init_db():
    """ডাটাবেস টেবিল তৈরি করে"""
    from . import models
    Base.metadata.create_all(bind=engine)
    print("✅ ডাটাবেস টেবিল তৈরি হয়েছে!")

def close_db():
    """ডাটাবেস কানেকশন বন্ধ করে"""
    engine.dispose()
    print("✅ ডাটাবেস কানেকশন বন্ধ হয়েছে")

def test_connection():
    """ডাটাবেস কানেকশন টেস্ট করে"""
    try:
        session = SessionLocal()
        session.execute("SELECT 1")
        session.close()
        print("✅ ডাটাবেস কানেকশন সফল!")
        return True
    except Exception as e:
        print(f"❌ ডাটাবেস কানেকশন ব্যর্থ: {e}")
        return False
