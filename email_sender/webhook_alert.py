import requests
import json

WEBHOOK_URL = "https://discord.com/api/webhooks/1513125500476719166/IDq1Q9VrWx55avkaHXXDaZlb7Qp7Xj9LlHLpucN9TBOUZ58wW9ZLqt8K3Qh4rCjtEZ3u"

def send_alert(company_name, mrr, score, accept_url, decline_url):
    """
    Sends a simple alert to Discord using Webhooks.
    """
    message = (
        f"🔴 **CHURN РИСК** — {company_name} | MRR: €{mrr} | Score: {score}/100\n\n"
        f"hello master — what do you decide?\n\n"
        f"✅ [Approve & Send Email]({accept_url})　　❌ [Decline]({decline_url})"
    )

    payload = {
        "content": message
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 204:
        print("✅ Успешно изпратено към Discord Webhook!")
    else:
        print(f"❌ Грешка при изпращане: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Тест на функцията
    send_alert(
        company_name="Acme Corp",
        mrr=2400,
        score=82,
        accept_url="http://localhost:5000/approve/acme_corp",
        decline_url="http://localhost:5000/decline/acme_corp"
    )
