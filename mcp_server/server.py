import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "ai_engine" / ".env")

try:
    import requests
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: ai_engine\\.venv\\Scripts\\pip.exe install mcp requests")
    sys.exit(1)

CLIENTS_FILE = Path(__file__).parent.parent / "clients.json"
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "")
LINKEDIN_API_KEY = os.getenv("REAL_LINKEDIN_API_KEY", "")
LINKEDIN_HOST = os.getenv("REAL_LINKEDIN_API_HOST", "fresh-linkedin-profile-data.p.rapidapi.com")

mcp = FastMCP("ChurnGuard")


def _load_clients() -> list:
    if CLIENTS_FILE.exists():
        return json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))
    return []


def _extract_linkedin_slug(url: str) -> str:
    """Extracts the username slug from a LinkedIn URL."""
    match = re.search(r"linkedin\.com/in/([^/?#]+)", url or "")
    return match.group(1).rstrip("/") if match else ""


# ── Tool 1: All clients ───────────────────────────────────────────────────────

@mcp.tool()
def get_clients() -> str:
    """Returns all monitored clients from the local ChurnGuard database."""
    clients = _load_clients()
    return json.dumps(clients, ensure_ascii=False, indent=2)


# ── Tool 2: HubSpot contact lookup ───────────────────────────────────────────

@mcp.tool()
def get_hubspot_contact(name: str, company: str) -> str:
    """
    Looks up a contact in HubSpot CRM by name and company.
    Falls back to local clients.json data if HubSpot is unreachable or unconfigured.

    Args:
        name: Full name of the contact (e.g. 'Тихомир Бахов')
        company: Company name (e.g. 'AdScout')
    """
    if HUBSPOT_API_KEY:
        try:
            url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            headers = {
                "Authorization": f"Bearer {HUBSPOT_API_KEY}",
                "Content-Type": "application/json",
            }
            first_name = name.split()[0] if name else name
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "firstname",
                                "operator": "CONTAINS_TOKEN",
                                "value": first_name,
                            }
                        ]
                    }
                ],
                "properties": [
                    "firstname", "lastname", "email", "company",
                    "hs_lead_status", "lifecyclestage", "phone",
                ],
                "limit": 5,
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    return json.dumps(
                        {"source": "hubspot", "contact": results[0]["properties"]},
                        ensure_ascii=False,
                        indent=2,
                    )
                return json.dumps(
                    {"source": "hubspot", "contact": None, "message": "No HubSpot match found"},
                    ensure_ascii=False,
                )
            print(f"[MCP] HubSpot returned {resp.status_code} — falling back")
        except Exception as e:
            print(f"[MCP] HubSpot error: {e} — falling back")

    # ── Fallback: local clients.json ─────────────────────────────────────────
    clients = _load_clients()
    name_lower = name.lower()
    company_lower = company.lower()
    for c in clients:
        if name_lower in c["name"].lower() or company_lower in c["company"].lower():
            return json.dumps(
                {
                    "source": "local_fallback",
                    "contact": {
                        "name": c["name"],
                        "company": c["company"],
                        "email": c["contact_email"],
                        "plan": c["current_plan"],
                        "mrr": c["mrr"],
                        "contract_end": c["contract_end"],
                    },
                },
                ensure_ascii=False,
                indent=2,
            )

    return json.dumps(
        {"source": "local_fallback", "contact": None, "message": "Not found locally either"},
        ensure_ascii=False,
    )


# ── Tool 3: LinkedIn signals ──────────────────────────────────────────────────

@mcp.tool()
def get_linkedin_signals(linkedin_url: str) -> str:
    """
    Fetches recent LinkedIn activity and signals for a profile.
    Falls back to stored signals from clients.json if the API is unavailable.

    Args:
        linkedin_url: Full LinkedIn profile URL (e.g. 'https://www.linkedin.com/in/tihobanov/')
    """
    # ── Try RapidAPI live data ────────────────────────────────────────────────
    if LINKEDIN_API_KEY:
        try:
            url = f"https://{LINKEDIN_HOST}/get-profile-posts"
            headers = {
                "X-RapidAPI-Key": LINKEDIN_API_KEY,
                "X-RapidAPI-Host": LINKEDIN_HOST,
            }
            resp = requests.get(
                url,
                headers=headers,
                params={"linkedin_url": linkedin_url},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get("data", []) if isinstance(data, dict) else data
                if isinstance(posts, list) and posts:
                    signals = []
                    for post in posts[:3]:
                        text = post.get("text") or post.get("postText")
                        if isinstance(post.get("commentary"), dict):
                            text = post["commentary"].get("text")
                        if text:
                            signals.append(
                                {"type": "growth", "severity": "medium", "detail": text.strip()}
                            )
                    if signals:
                        return json.dumps(
                            {
                                "source": "linkedin_live",
                                "linkedin_url": linkedin_url,
                                "signals": signals,
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
            print(f"[MCP] LinkedIn API returned {resp.status_code} — falling back")
        except Exception as e:
            print(f"[MCP] LinkedIn error: {e} — falling back")

    # ── Fallback: match by slug in clients.json ───────────────────────────────
    target_slug = _extract_linkedin_slug(linkedin_url)
    clients = _load_clients()
    for c in clients:
        if target_slug and target_slug == _extract_linkedin_slug(c.get("linkedin", "")):
            return json.dumps(
                {
                    "source": "local_fallback",
                    "linkedin_url": linkedin_url,
                    "person_name": c["name"],
                    "company": c["company"],
                    "signals": c.get("signals", []),
                },
                ensure_ascii=False,
                indent=2,
            )

    # ── Generic demo fallback ─────────────────────────────────────────────────
    return json.dumps(
        {
            "source": "demo_fallback",
            "linkedin_url": linkedin_url,
            "signals": [
                {
                    "type": "growth",
                    "severity": "low",
                    "detail": "No live API key configured — demo signal only.",
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


# ── Tool 4: Full client enrichment ───────────────────────────────────────────

@mcp.tool()
def get_client_data(client_id: int) -> str:
    """
    Returns enriched data for a client: local info + HubSpot CRM + LinkedIn signals.

    Args:
        client_id: Numeric client ID from clients.json (e.g. 1, 2, 3)
    """
    clients = _load_clients()
    client = next((c for c in clients if c["id"] == client_id), None)
    if not client:
        return json.dumps({"error": f"Client {client_id} not found"})

    crm = json.loads(get_hubspot_contact(client["name"], client["company"]))
    linkedin = json.loads(get_linkedin_signals(client.get("linkedin", "")))

    return json.dumps(
        {"client": client, "crm": crm, "linkedin": linkedin},
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    print("[MCP] ChurnGuard MCP server starting (stdio mode)...")
    print(f"[MCP] HubSpot: {'configured' if HUBSPOT_API_KEY else 'NOT configured (will use local fallback)'}")
    print(f"[MCP] LinkedIn: {'configured' if LINKEDIN_API_KEY else 'NOT configured (will use local fallback)'}")
    mcp.run()
