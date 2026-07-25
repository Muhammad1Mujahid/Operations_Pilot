import sqlite3
from datetime import datetime


DB_Name = "Health_mointer.db"

def init_db():
    conn = sqlite3.connect(DB_Name)
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
                   create table if not exists Incident_Reports (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       cpu_usage REAL,
                       disk_usage REAL,
                       memory_usage REAL
                   )
                   ''')
    conn.commit()
    conn.close()



def insert_to_health_metrics(cpu_usage, disk_usage, memory_usage):
    conn = sqlite3.connect(DB_Name)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT Into health_metrics (cpu_usage, disk_usage, memory_usage)
                   VALUES (?, ?, ?)
                   ''', (cpu_usage, disk_usage, memory_usage))
    conn.commit()
    conn.close()

def insert_to_incident_reports(cpu_usage, disk_usage, memory_usage):
    conn = sqlite3.connect(DB_Name)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT Into Incident_Reports (cpu_usage, disk_usage, memory_usage)
                   VALUES (?, ?, ?)
                   ''', (cpu_usage, disk_usage, memory_usage))
    #cursor.fetchall()  # Fetch all results to ensure the query is executed
    conn.commit()
    conn.close()

    