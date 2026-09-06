from fastapi import FastAPI, WebSocket
from database import DB_NAME
from fastapi.staticfiles import StaticFiles
import asyncio
import sqlite3

app = FastAPI()

app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")


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
    cursor.execute("SELECT * FROM incidents ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_latest_metric():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_metrics ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


@app.websocket("/ws/live-status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    last_sent_id = None

    try:
        while True:
            latest = get_latest_metric()

            if latest and latest["id"] != last_sent_id:
                await websocket.send_json(latest)
                last_sent_id = latest["id"]

            await asyncio.sleep(2)   # check DB every 2s for a new row
    except Exception:
        pass
