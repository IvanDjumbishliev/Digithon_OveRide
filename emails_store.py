"""Shared email store — read and update alerts from emails.json.

The Discord bot (email_sender) imports this module to:
1. Get pending emails that need to be sent
2. Mark them as sent after successful delivery
"""

import json
from pathlib import Path

EMAILS_FILE = Path(__file__).parent / "emails.json"


def get_pending_emails() -> list[dict]:
    """Return all alerts with status 'pending'."""
    alerts = _load()
    return [a for a in alerts if a.get("status") == "pending"]


def mark_as_sent(alert_id: str) -> bool:
    """Mark an alert as sent. Returns True if found and updated."""
    alerts = _load()
    for alert in alerts:
        if alert["id"] == alert_id:
            alert["status"] = "sent"
            _save(alerts)
            return True
    return False


def mark_as_failed(alert_id: str, reason: str = "") -> bool:
    """Mark an alert as failed. Returns True if found and updated."""
    alerts = _load()
    for alert in alerts:
        if alert["id"] == alert_id:
            alert["status"] = "failed"
            alert["fail_reason"] = reason
            _save(alerts)
            return True
    return False


def get_all_emails() -> list[dict]:
    """Return all alerts regardless of status."""
    return _load()


def _load() -> list[dict]:
    if not EMAILS_FILE.exists():
        return []
    try:
        return json.loads(EMAILS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return []


def _save(alerts: list[dict]) -> None:
    EMAILS_FILE.write_text(json.dumps(alerts, ensure_ascii=False, indent=2), encoding="utf-8")
