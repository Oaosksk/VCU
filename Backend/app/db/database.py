"""Database connection — supports both SQLite and MySQL"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models import Base

# SQLite needs check_same_thread=False for FastAPI's threading model.
# MySQL does not need this and uses connection pooling instead.
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # MySQL via XAMPP — pool_pre_ping checks connection health on each use
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,   # recycle connections every 1 hour
        pool_size=5,
        max_overflow=10,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency-injected database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
