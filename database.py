import sqlite3
import os

DB_NAME = os.path.join("data", "Health_moniter.db")

def add_ai_columns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for column in ["suggested_cause TEXT", "suggested_fix TEXT"]:
        try:
            cursor.execute(f"ALTER TABLE incidents ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass  # column already exists — safe to ignore
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_usage REAL,
            disk_usage REAL,
            memory_usage REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            severity TEXT,
            server TEXT,
            metric_value REAL,
            detected_at TEXT,
            resolved_at TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()
    add_ai_columns()   # ← new line, added after table creation


def insert_to_health_metrics(cpu_usage, disk_usage, memory_usage):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_metrics (cpu_usage, disk_usage, memory_usage)
        VALUES (?, ?, ?)
    ''', (cpu_usage, disk_usage, memory_usage))
    conn.commit()
    conn.close()

def update_incident_ai_suggestion(incident_id, cause, fix):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE incidents SET suggested_cause = ?, suggested_fix = ?
        WHERE id = ?
    ''', (cause, fix, incident_id))
    conn.commit()
    conn.close()