import smtplib
import time
from email.mime.text import MIMEText
from notifications.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_TO

# Rate-limiting: track last-sent time per incident type
_last_sent = {}
RATE_LIMIT_SECONDS = 300  # don't re-alert same type within 5 minutes


def send_alert(incident_type, severity, server, value):
    now = time.time()
    last = _last_sent.get(incident_type, 0)

    if now - last < RATE_LIMIT_SECONDS:
        return  # too soon since last alert for this type — skip

    subject = f"[OpsPilot] {severity} - {incident_type} on {server}"
    body = (
        f"{incident_type} usage reached {value}%.\n"
        f"Severity: {severity}\n"
        f"Server: {server}\n"
        f"View dashboard: http://localhost:8000/dashboard/\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server_conn:
            server_conn.starttls()
            server_conn.login(SMTP_USER, SMTP_PASSWORD)
            server_conn.sendmail(SMTP_USER, ALERT_TO, msg.as_string())
        _last_sent[incident_type] = now
    except Exception as e:
        print(f"Failed to send alert email: {e}")
