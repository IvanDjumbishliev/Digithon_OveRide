"""Signal analysis module — uses OpenRouter to classify LinkedIn signals as churn risk or upsell opportunity."""

import json
import logging
import os
import re
import time

import requests

from ai_engine.prompts import ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemma-3-4b-it:free"

_DEFAULT_RESULT = {
    "type": "unknown",
    "score": 50,
    "explanation": "Не можах да анализирам сигналите",
}


def _call_llm(prompt: str) -> str:
    """Send a prompt to OpenRouter and return the response text."""
    headers = {
        "Authorization": f"Bearer {os.environ['OPEN_ROUTER_KEY']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def format_signals(signals: list) -> str:
    """Format a list of signal dicts into readable text for the prompt."""
    lines = []
    for s in signals:
        severity = s.get("severity", "unknown")
        lines.append(f"- [{s['type'].upper()}] (severity: {severity}) {s['detail']}")
    return "\n".join(lines)


def _extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from text using regex fallback."""
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def analyze_signals(client_data: dict, signals: list) -> dict:
    """Analyze LinkedIn signals for a client and return classification with score.

    Returns a dict with keys: type, score, explanation.
    """
    signals_text = format_signals(signals)

    prompt = ANALYSIS_PROMPT.format(
        product_name=client_data["our_product"],
        company=client_data["company"],
        contact_name=client_data["contact_name"],
        plan=client_data["current_plan"],
        mrr=client_data["mrr"],
        contract_end=client_data["contract_end"],
        signals_text=signals_text,
    )

    last_error = None
    for attempt in range(1, 4):
        try:
            text = _call_llm(prompt)
            logger.debug("LLM raw response: %s", text)

            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                logger.warning("Direct JSON parse failed, attempting regex extraction")
                result = _extract_json(text)
                if result is None:
                    raise ValueError("Could not parse JSON from response")

            if "type" not in result or "score" not in result:
                raise ValueError("Response missing required fields")

            return {
                "type": result["type"],
                "score": int(result["score"]),
                "explanation": result.get("explanation", ""),
            }

        except Exception as e:
            last_error = e
            logger.warning("Attempt %d/3 failed: %s", attempt, e)
            if attempt < 3:
                time.sleep(2)

    logger.error("All attempts failed. Last error: %s", last_error)
    return dict(_DEFAULT_RESULT)


def should_alert(analysis: dict, threshold: int = 50) -> bool:
    """Return True if the analysis score meets or exceeds the threshold."""
    return analysis.get("score", 0) >= threshold
