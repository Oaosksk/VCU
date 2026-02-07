"""Initialize database"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import init_db as create_tables
from app.core.config import settings

def init_db():
    print(f"Initializing database at {settings.DATABASE_URL}")
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
