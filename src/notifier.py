import requests
import os

def send_telegram_digest(chat_id, opportunities):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token or not opportunities: return
    
    message = "📅 **Resumo de Oportunidades de Hoje**\n\n"
    for opp in opportunities[:5]:
        message += f"📌 *{opp['title']}*\n"
        message += f"🔗 {opp['url']}\n"
        message += f"🏢 Fonte: {opp['source']}\n\n"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)
