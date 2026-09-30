import sqlite3
import pytest
import incidents.detector as detector


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Creates a fresh, temporary SQLite database with the same schema
    as the real one, and points the detector module at it instead
    of the real database — so tests never touch real data.
    """
    db_path = tmp_path / "test.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            severity TEXT,
            server TEXT,
            metric_value REAL,
            detected_at TEXT,
            resolved_at TEXT,
            status TEXT,
            suggested_cause TEXT,
            suggested_fix TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # Point the detector module's DB_NAME at our temporary test database
    monkeypatch.setattr(detector, "DB_NAME", str(db_path))

    # Replace real email/AI calls with no-ops during tests —
    # we're testing incident logic, not SMTP or Gemini
    monkeypatch.setattr(detector, "send_alert", lambda *args, **kwargs: None)
    monkeypatch.setattr(detector, "suggest_root_cause", lambda *args, **kwargs: ("", ""))

    return str(db_path)
