import sqlite3
from incidents.detector import check_and_record


def count_incidents(db_path, status=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT COUNT(*) FROM incidents")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def test_creates_incident_on_critical_value(test_db):
    check_and_record("CPU", 96)
    assert count_incidents(test_db) == 1
    assert count_incidents(test_db, status="OPEN") == 1


def test_idempotent_does_not_duplicate(test_db):
    # Simulates the metric staying critical across multiple loop passes
    check_and_record("CPU", 96)
    check_and_record("CPU", 97)
    check_and_record("CPU", 96)
    assert count_incidents(test_db) == 1  # still just one incident, not three


def test_auto_resolves_when_healthy_again(test_db):
    check_and_record("CPU", 96)   # creates incident
    check_and_record("CPU", 30)   # recovers
    assert count_incidents(test_db, status="OPEN") == 0
    assert count_incidents(test_db, status="RESOLVED") == 1


def test_healthy_value_creates_no_incident(test_db):
    check_and_record("Memory", 10)
    assert count_incidents(test_db) == 0
