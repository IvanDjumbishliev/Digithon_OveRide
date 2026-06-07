"""Email generation module — drafts personalized outreach emails based on signal analysis."""

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

from ai_engine.analyzer import analyze_signals, should_alert, _call_llm, _extract_json
from ai_engine.prompts import EMAIL_PROMPT
from email_sender.webhook_alert import send_alert as send_discord_alert

logger = logging.getLogger(__name__)

_FORBIDDEN_WORDS = ["linkedin", "профил", "постове"]

EMAILS_FILE = Path(__file__).parent.parent / "emails.json"


def save_alert(alert: dict) -> None:
    """Append an alert to emails.json."""
    alerts = []
    if EMAILS_FILE.exists():
        try:
            alerts = json.loads(EMAILS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            alerts = []
    alerts.append(alert)
    EMAILS_FILE.write_text(json.dumps(alerts, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Alert %s saved to %s", alert["id"], EMAILS_FILE)


def _contains_forbidden(body: str) -> bool:
    """Check if the email body contains any forbidden words."""
    lower = body.lower()
    return any(word in lower for word in _FORBIDDEN_WORDS)


def summarize_signals(signals: list) -> str:
    """Condense a list of signal dicts into a 1-2 sentence summary."""
    if not signals:
        return "Няма налични сигнали."

    types = [s["type"] for s in signals]
    details = [s["detail"] for s in signals]

    type_counts = {}
    for t in types:
        type_counts[t] = type_counts.get(t, 0) + 1

    parts = []
    for signal_type, count in type_counts.items():
        if count > 1:
            parts.append(f"{count}x {signal_type}")
        else:
            parts.append(signal_type)

    summary = f"Засечени сигнали: {', '.join(parts)}. "
    summary += details[0]
    if len(details) > 1:
        summary += f" Също: {details[1]}"

    return summary


def generate_email(
    client_data: dict, signals: list, analysis: dict, language: str = "bg"
) -> dict:
    """Generate a personalized email draft using OpenRouter.

    Returns a dict with keys: subject, body.
    """
    signals_summary = summarize_signals(signals)

    prompt = EMAIL_PROMPT.format(
        product_name=client_data["our_product"],
        company=client_data["company"],
        contact_name=client_data["contact_name"],
        plan=client_data["current_plan"],
        mrr=client_data["mrr"],
        contract_end=client_data["contract_end"],
        alert_type=analysis["type"],
        signals_summary=signals_summary,
        explanation=analysis["explanation"],
        language=language,
    )

    fallback = {
        "subject": f"Следваща стъпка за {client_data['company']}",
        "body": (
            f"Здравей {client_data['contact_name']}, бих искал да обсъдим как можем "
            f"да ви помогнем. Имате ли 20 минути тази седмица?"
        ),
    }

    last_error = None
    for attempt in range(1, 4):
        try:
            text = _call_llm(prompt)
            logger.debug("LLM email response: %s", text)

            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                logger.warning("Direct JSON parse failed, attempting regex extraction")
                result = _extract_json(text)
                if result is None:
                    raise ValueError("Could not parse JSON from response")

            if "subject" not in result or "body" not in result:
                raise ValueError("Response missing required fields")

            if _contains_forbidden(result["body"]):
                logger.warning("Forbidden word detected in body, requesting regeneration")
                retry_prompt = (
                    prompt
                    + "\n\nВАЖНО: Предишният отговор съдържаше забранена дума. "
                    "НЕ споменавай LinkedIn, профил или постове. "
                    "Генерирай нов имейл без тези думи."
                )
                text = _call_llm(retry_prompt)

                try:
                    result = json.loads(text)
                except json.JSONDecodeError:
                    result = _extract_json(text)
                    if result is None:
                        raise ValueError("Could not parse regenerated JSON")

                if _contains_forbidden(result.get("body", "")):
                    logger.error("Forbidden word persists after regeneration, using fallback")
                    return dict(fallback)

            return {"subject": result["subject"], "body": result["body"]}

        except Exception as e:
            last_error = e
            logger.warning("Email generation attempt %d/3 failed: %s", attempt, e)
            if attempt < 3:
                time.sleep(2)

    logger.error("All email generation attempts failed. Last error: %s", last_error)
    return dict(fallback)


def build_alert(
    client_data: dict, signals: list, analysis: dict, email: dict
) -> dict:
    """Assemble the final alert object combining all pipeline outputs."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_uid = uuid.uuid4().hex[:6]

    return {
        "id": f"alert_{today}_{short_uid}",
        "type": analysis["type"],
        "score": analysis["score"],
        "company": client_data["company"],
        "contact_name": client_data["contact_name"],
        "contact_email": client_data["contact_email"],
        "mrr": client_data["mrr"],
        "signals": signals,
        "explanation": analysis["explanation"],
        "draft_subject": email["subject"],
        "draft_body": email["body"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def process_client(
    client_data: dict, signals: list, threshold: int = 50
) -> dict | None:
    """Full pipeline: analyze signals, generate email, build alert.

    Returns the alert dict if score meets threshold, otherwise None.
    """
    analysis = analyze_signals(client_data, signals)
    logger.info(
        "Analysis for %s: type=%s score=%d",
        client_data["company"],
        analysis["type"],
        analysis["score"],
    )

    if not should_alert(analysis, threshold):
        logger.info("Score %d below threshold %d, skipping", analysis["score"], threshold)
        return None

    email = generate_email(client_data, signals, analysis)
    alert = build_alert(client_data, signals, analysis, email)
    save_alert(alert)

    try:
        send_discord_alert(
            company_name=client_data["company"],
            mrr=client_data["mrr"],
            score=analysis["score"],
            accept_url=f"http://localhost:5000/approve/{alert['id']}",
            decline_url=f"http://localhost:5000/decline/{alert['id']}",
            email_subject=email["subject"],
            email_body=email["body"],
        )
    except Exception as e:
        logger.error("Discord notification failed: %s", e)

    logger.info("Alert created: %s (score: %d)", alert["id"], alert["score"])
    return alert
