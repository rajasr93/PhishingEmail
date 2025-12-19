import sqlite3
import json
import time
import os
from enum import Enum
from config import DB_PATH

class TaskStatus(Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    DONE = "DONE"
    FAILED = "FAILED"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_queue (
            id TEXT PRIMARY KEY,
            headers TEXT,
            body TEXT,
            status TEXT DEFAULT 'PENDING',
            risk_score INTEGER DEFAULT 0,
            analysis_report TEXT,
            created_at REAL,
            updated_at REAL
        )
    ''')
    conn.commit()
    conn.close()

def push_email_to_queue(email_id, headers, body):
    """Producer: Adds email to queue [cite: 13, 92]"""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO email_queue (id, headers, body, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (email_id, json.dumps(headers), body, TaskStatus.PENDING.value, time.time())
        )
        print(f"[Queue] Email {email_id} added.")
    except sqlite3.IntegrityError:
        print(f"[Queue] Email {email_id} already exists.")
    finally:
        conn.close()

def fetch_next_job():
    """Consumer: Fetches oldest PENDING job"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, headers, body FROM email_queue WHERE status='PENDING' ORDER BY created_at ASC LIMIT 1")
        row = cur.fetchone()
        if row:
            conn.execute("UPDATE email_queue SET status=?, updated_at=? WHERE id=?", 
                         (TaskStatus.ANALYZING.value, time.time(), row[0]))
            conn.commit()
            return row
    finally:
        conn.close()
    return None

def mark_job_complete(email_id, risk_score, report):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE email_queue SET status=?, risk_score=?, analysis_report=?, updated_at=? WHERE id=?",
        (TaskStatus.DONE.value, risk_score, json.dumps(report), time.time(), email_id)
    )
    conn.commit()
    conn.close()

def update_status(email_id, status):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE email_queue SET status=?, updated_at=? WHERE id=?", (status, time.time(), email_id))
    conn.commit()
    conn.close()