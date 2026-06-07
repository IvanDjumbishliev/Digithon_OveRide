import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from flask import Flask

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "ai_engine", ".env"))

from emails_store import get_pending_emails, mark_as_sent, mark_as_failed
from email_sender.webhook_alert import send_alert as send_discord_alert

app = Flask(__name__)

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")


def _send_email(to_addr: str, subject: str, body: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_addr, msg.as_string())


@app.route("/approve/<alert_id>")
def approve(alert_id):
    alerts = get_pending_emails()
    alert = next((a for a in alerts if a["id"] == alert_id), None)

    if not alert:
        return f"<h2>Alert {alert_id} not found or already processed.</h2>", 404

    try:
        _send_email(alert["contact_email"], alert["draft_subject"], alert["draft_body"])
        mark_as_sent(alert_id)
        send_discord_alert(
            company_name=alert["company"],
            mrr=alert["mrr"],
            score=alert["score"],
            accept_url="",
            decline_url="",
            email_subject=alert["draft_subject"],
            email_body=f"✅ APPROVED & SENT to {alert['contact_email']}",
        )
        return f"<h2>Email sent to {alert['contact_email']}!</h2><p>Subject: {alert['draft_subject']}</p>"
    except Exception as e:
        mark_as_failed(alert_id, str(e))
        return f"<h2>Failed to send email</h2><p>{e}</p>", 500


@app.route("/decline/<alert_id>")
def decline(alert_id):
    alerts = get_pending_emails()
    alert = next((a for a in alerts if a["id"] == alert_id), None)

    if not alert:
        return f"<h2>Alert {alert_id} not found or already processed.</h2>", 404

    mark_as_failed(alert_id, "declined")
    send_discord_alert(
        company_name=alert["company"],
        mrr=alert["mrr"],
        score=alert["score"],
        accept_url="",
        decline_url="",
        email_subject=alert["draft_subject"],
        email_body="❌ DECLINED — email was NOT sent.",
    )
    return f"<h2>Alert {alert_id} declined.</h2>"


if __name__ == "__main__":
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("ERROR: Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables!")
        sys.exit(1)
    print(f"Server starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
