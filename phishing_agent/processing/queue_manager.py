import sqlite3
from enum import Enum
from config import DB_PATH

class TaskStatus(Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    DONE = "DONE"
    FAILED = "FAILED"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Schema supports v2 state tracking [cite: 37]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_queue (
            id TEXT PRIMARY KEY,
            raw_content TEXT,
            status TEXT,
            result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def push_email(email_id, content):
    """Producer: Adds email to persistent local queue [cite: 13]"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR IGNORE INTO email_queue (id, raw_content, status) VALUES (?, ?, ?)",
                 (email_id, content, TaskStatus.PENDING.value))
    conn.commit()
    conn.close()