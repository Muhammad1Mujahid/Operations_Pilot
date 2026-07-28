import sqlite3

DB_NAME = "Health_moniter.db"


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


def insert_to_health_metrics(cpu_usage, disk_usage, memory_usage):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_metrics (cpu_usage, disk_usage, memory_usage)
        VALUES (?, ?, ?)
    ''', (cpu_usage, disk_usage, memory_usage))
    conn.commit()
    conn.close()