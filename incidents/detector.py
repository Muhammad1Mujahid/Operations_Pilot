import sqlite3
from datetime import datetime
from incidents.severity import get_severity
from notifications.notifier import send_alert
from ai.analyzer import suggest_root_cause
from database import update_incident_ai_suggestion

DB_NAME = "Health_moniter.db"


def get_open_incident(conn, incident_type):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE type = ? AND status = 'OPEN'",
        (incident_type,)
    )
    return cursor.fetchone()


def create_incident(conn, incident_type, severity, server, value):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (type, severity, server, metric_value, detected_at, status)
        VALUES (?, ?, ?, ?, ?, 'OPEN')
    ''', (incident_type, severity, server, value, datetime.now().isoformat()))
    conn.commit()
    return cursor.lastrowid   # ← new line: returns the new incident's id


def resolve_incident(conn, incident_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE incidents SET status = 'RESOLVED', resolved_at = ?
        WHERE id = ?
    ''', (datetime.now().isoformat(), incident_id))
    conn.commit()


def check_and_record(incident_type, value, server="Ubuntu-01"):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    severity = get_severity(value)
    existing = get_open_incident(conn, incident_type)

    if severity:
        if not existing:
            incident_id = create_incident(conn, incident_type, severity, server, value)
            send_alert(incident_type, severity, server, value)

            cause, fix = suggest_root_cause(incident_type, severity, server, value)
            if cause or fix:
                update_incident_ai_suggestion(incident_id, cause, fix)
        # else: already open — idempotency, do nothing
    else:
        if existing:
            resolve_incident(conn, existing["id"])

    conn.close()