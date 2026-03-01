# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file
DATABASE_URL = "sqlite:///./app.db"

# SQLAlchemy engine (sync)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed only for SQLite
)

# SessionLocal for DB operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()