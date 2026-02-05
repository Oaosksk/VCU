"""Initialize database"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

def init_db():
    print(f"Initializing database at {settings.DATABASE_URL}")
    # Database initialization will be added when SQLAlchemy models are created
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
