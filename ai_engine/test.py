# test_ai_engine.py
import os
import sys
import asyncio
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai_engine.email_generator import process_client

test_client = {
    "company": "ABC Corp",
    "contact_name": "Иван Петров",
    "contact_email": "ivan@abccorp.com",
    "linkedin_url": "https://linkedin.com/in/ivan-petrov",
    "current_plan": "Basic",
    "mrr": 2000,
    "contract_end": "2026-09-15",
    "our_product": "DataSync Pro"
}

test_signals = [
    {"type": "hiring", "severity": "medium", "detail": "5 job posts за developers тази седмица"},
    {"type": "growth", "severity": "medium", "detail": "Пост за нов офис в Лондон"}
]

result = asyncio.run(process_client(test_client, test_signals))
if result:
    print("Alert created successfully!")
    print(f"  ID: {result['id']}")
    print(f"  Type: {result['type']}")
    print(f"  Score: {result['score']}")
    print(f"  Explanation: {result['explanation']}")
    print(f"  Subject: {result['draft_subject']}")
    print(f"  Body: {result['draft_body']}")
else:
    print("No alert generated (score below threshold)")
