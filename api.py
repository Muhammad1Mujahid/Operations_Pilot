from fastapi import FastAPI
import sqlite3

app = FastAPI()
DB_NAME = "Health_mointer.db"   # match your exact existing filename


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row   # lets us access columns by name, not just index
    return conn


@app.get("/system-status")
def system_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_metrics ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"message": "No data yet"}

    return dict(row)


@app.get("/history")
def history(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_metrics ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.get("/incidents")
def incidents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incident_reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
