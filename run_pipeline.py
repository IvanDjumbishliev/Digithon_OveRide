"""Full pipeline — reads clients from clients.json, rewrites emails.json with fresh alerts.

Usage:
    python run_pipeline.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "ai_engine", ".env"))

from ai_engine.email_generator import process_client, EMAILS_FILE

CLIENTS_FILE = Path(__file__).parent / "clients.json"


async def main():
    if not CLIENTS_FILE.exists():
        print("clients.json not found. Add clients via the frontend first.")
        return

    clients = json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))

    if not clients:
        print("No clients in clients.json. Add clients via the frontend first.")
        return

    # One email per company — pick highest MRR representative
    seen: set[str] = set()
    unique_clients = []
    for c in sorted(clients, key=lambda x: x.get("id", 0)):
        if c["company"] not in seen:
            seen.add(c["company"])
            unique_clients.append(c)
    clients = unique_clients

    print("=" * 50)
    print(f"  ChurnGuard Pipeline — {len(clients)} companies")
    print("=" * 50)

    # Fresh run — clear previous alerts
    EMAILS_FILE.write_text("[]", encoding="utf-8")

    results = []
    for client in clients:
        signals = client.get("signals", [])
        if not signals:
            print(f"\n[{client['id']}] {client['name']} @ {client['company']} — no signals, skipping")
            continue

        print(f"\n[{client['id']}] {client['name']} @ {client['company']}")

        client_data = {
            "company": client["company"],
            "contact_name": client["name"],
            "contact_email": client["contact_email"],
            "linkedin_url": client["linkedin"],
            "current_plan": client["current_plan"],
            "mrr": client["mrr"],
            "contract_end": client["contract_end"],
            "our_product": client["our_product"],
        }

        result = await process_client(client_data, signals)

        if result:
            print(f"  Type: {result['type']} | Score: {result['score']}")
            print(f"  Subject: {result['draft_subject']}")
            print(f"  Discord notified.")
            results.append(result)
        else:
            print(f"  Score below threshold, skipped.")

    print("\n" + "=" * 50)
    print(f"  Done. {len(results)}/{len(clients)} alerts generated.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
