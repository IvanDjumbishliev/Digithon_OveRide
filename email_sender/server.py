import json
import os
import re
import smtplib
import subprocess
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from urllib.parse import urlencode
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "ai_engine", ".env"))

from emails_store import get_pending_emails, mark_as_sent, mark_as_failed
from email_sender.webhook_alert import send_alert as send_discord_alert

app = Flask(__name__)
CORS(app)

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
CLIENTS_FILE = Path(__file__).parent.parent / "clients.json"
FRONTEND_URL = "http://localhost:5173"

_CHURN_TYPES = {"competitor_engagement", "silence", "job_change"}
_UPSELL_TYPES = {"hiring", "growth"}


# ── clients.json helpers ──────────────────────────────────────────────────────

def _load_clients() -> list:
    if not CLIENTS_FILE.exists():
        return []
    return json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))


def _save_clients(clients: list) -> None:
    CLIENTS_FILE.write_text(json.dumps(clients, ensure_ascii=False, indent=2), encoding="utf-8")


def _signal_for_client(client: dict) -> str:
    types = {s["type"] for s in client.get("signals", [])}
    if types & _CHURN_TYPES:
        return "churn"
    if types & _UPSELL_TYPES:
        return "upsell"
    return "neutral"


# ── API: clients ──────────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def api_get_users():
    clients = _load_clients()
    users = [
        {
            "id": c["id"],
            "name": c["name"],
            "company": c["company"],
            "linkedin": c["linkedin"],
            "signal": _signal_for_client(c),
            "lastScan": "just now",
        }
        for c in clients
    ]
    return jsonify(users)


@app.route("/api/users", methods=["POST"])
def api_add_user():
    data = request.get_json()
    clients = _load_clients()
    new_id = max((c["id"] for c in clients), default=0) + 1
    new_client = {
        "id": new_id,
        "name": data["name"],
        "company": data["company"],
        "linkedin": data["linkedin"],
        "contact_email": "mdimitrov1239@gmail.com",
        "mrr": 0,
        "current_plan": "Basic",
        "contract_end": "2027-01-01",
        "our_product": "OveRide Signal",
        "signals": [],
    }
    clients.append(new_client)
    _save_clients(clients)
    return jsonify({"id": new_id, "name": new_client["name"], "company": new_client["company"],
                    "linkedin": new_client["linkedin"], "signal": "neutral", "lastScan": "Just added"}), 201


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    clients = _load_clients()
    clients = [c for c in clients if c["id"] != user_id]
    _save_clients(clients)
    return jsonify({"ok": True})


# ── email sending ─────────────────────────────────────────────────────────────

def _send_email(to_addr: str, subject: str, body: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_addr, msg.as_string())


# ── approve / decline ─────────────────────────────────────────────────────────

@app.route("/approve/<alert_id>")
def approve(alert_id):
    alerts = get_pending_emails()
    alert = next((a for a in alerts if a["id"] == alert_id), None)

    if not alert:
        return redirect(f"{FRONTEND_URL}?{urlencode({'status': 'error', 'company': '', 'contact': '', 'subject': 'Alert not found', 'score': ''})}")

    try:
        _send_email(alert["contact_email"], alert["draft_subject"], alert["draft_body"])
        mark_as_sent(alert_id)
        send_discord_alert(
            company_name=alert["company"],
            mrr=alert["mrr"],
            score=alert["score"],
            accept_url="", decline_url="",
            email_subject=alert["draft_subject"],
            email_body=f"✅ APPROVED & SENT to {alert['contact_email']}",
        )
    except Exception as e:
        mark_as_failed(alert_id, str(e))

    return redirect(f"{FRONTEND_URL}?{urlencode({'status': 'approved', 'company': alert['company'], 'contact': alert['contact_name'], 'subject': alert['draft_subject'], 'score': alert['score'], 'sentTo': alert['contact_email']})}")


@app.route("/decline/<alert_id>")
def decline(alert_id):
    alerts = get_pending_emails()
    alert = next((a for a in alerts if a["id"] == alert_id), None)

    if not alert:
        return redirect(f"{FRONTEND_URL}?{urlencode({'status': 'error', 'company': '', 'contact': '', 'subject': 'Alert not found', 'score': ''})}")

    mark_as_failed(alert_id, "declined")
    send_discord_alert(
        company_name=alert["company"],
        mrr=alert["mrr"],
        score=alert["score"],
        accept_url="", decline_url="",
        email_subject=alert["draft_subject"],
        email_body="❌ DECLINED — email was NOT sent.",
    )
    return redirect(f"{FRONTEND_URL}?{urlencode({'status': 'declined', 'company': alert['company'], 'contact': alert['contact_name'], 'subject': alert['draft_subject'], 'score': alert['score']})}")


@app.route("/api/run-pipeline", methods=["POST"])
def api_run_pipeline():
    try:
        pipeline_path = str(Path(__file__).parent.parent / "run_pipeline.py")
        result = subprocess.run(
            [sys.executable, pipeline_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            cwd=str(Path(__file__).parent.parent),
        )
        output = result.stdout + result.stderr
        m = re.search(r"(\d+)/(\d+) alerts generated", output)
        alerts = int(m.group(1)) if m else 0
        clients = int(m.group(2)) if m else 0
        return jsonify({"ok": True, "alerts": alerts, "clients": clients})
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Pipeline timed out"}), 504
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("ERROR: Set GMAIL_USER and GMAIL_APP_PASSWORD in ai_engine/.env")
        sys.exit(1)
    print("Server starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
