"""Fix database schema by adding missing columns"""
import sqlite3

db_path = "accident_detection.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE videos ADD COLUMN duration REAL DEFAULT NULL")
    print("Added duration column")
except sqlite3.OperationalError as e:
    print(f"duration: {e}")

try:
    cursor.execute("ALTER TABLE videos ADD COLUMN fps REAL DEFAULT NULL")
    print("Added fps column")
except sqlite3.OperationalError as e:
    print(f"fps: {e}")

try:
    cursor.execute("ALTER TABLE videos ADD COLUMN resolution VARCHAR(20) DEFAULT NULL")
    print("Added resolution column")
except sqlite3.OperationalError as e:
    print(f"resolution: {e}")

conn.commit()
conn.close()
print("Database schema updated successfully")
