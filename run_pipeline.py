"""Full pipeline: processes all clients from linkedin_monitor/clients.py.

Rewrites emails.json with fresh alerts and sends Discord notifications.

Usage:
    python run_pipeline.py
"""

import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "ai_engine", ".env"))

from pathlib import Path
from linkedin_monitor.clients import CLIENTS
from ai_engine.email_generator import process_client, EMAILS_FILE


async def main():
    print("=" * 50)
    print("  ChurnGuard Pipeline")
    print(f"  Processing {len(CLIENTS)} clients...")
    print("=" * 50)

    # Clear emails.json before fresh run
    EMAILS_FILE.write_text("[]", encoding="utf-8")

    results = []
    for client in CLIENTS:
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

        result = await process_client(client_data, client["signals"])

        if result:
            print(f"  Type: {result['type']} | Score: {result['score']}")
            print(f"  Subject: {result['draft_subject']}")
            print(f"  Discord notified.")
            results.append(result)
        else:
            print(f"  Score below threshold, skipped.")

    print("\n" + "=" * 50)
    print(f"  Done. {len(results)}/{len(CLIENTS)} alerts generated.")
    print(f"  Check Discord for notifications.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
