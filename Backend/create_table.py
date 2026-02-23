import sqlite3

conn = sqlite3.connect('accident_detection.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trained_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_type TEXT NOT NULL,
    model_path TEXT NOT NULL,
    training_date TEXT NOT NULL,
    total_videos INTEGER NOT NULL,
    accident_videos INTEGER NOT NULL,
    normal_videos INTEGER NOT NULL,
    accuracy REAL,
    loss REAL,
    epochs INTEGER,
    batch_size INTEGER,
    learning_rate REAL,
    feature_shape TEXT,
    notes TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Table created successfully!")
