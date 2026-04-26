import requests
import os

def send_telegram_digest(chat_id, opportunities):
    """(Legacy) Envia resumo via Telegram"""
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

def send_proactive_alert(opportunity):
    """
    Envia um alerta de elite (Score > 90%) para o Discord via Webhook.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    color = 0x2ecc71 # Verde para elite
    payload = {
        "embeds": [{
            "title": f"🚨 ELITE OPPORTUNITY FOUND! ({opportunity['score']}%)",
            "description": f"**{opportunity['title']}**\n\n{opportunity['rationale']}",
            "url": opportunity['url'],
            "color": color,
            "fields": [
                {"name": "Source", "value": opportunity['source'], "inline": True},
                {"name": "Type", "value": opportunity.get('type', 'Hackathon'), "inline": True}
            ],
            "footer": {"text": "Sent by Proactive Radar 🛰️"}
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print(f"📡 Alerta enviado com sucesso para o Discord: {opportunity['title']}")
    except Exception as e:
        print(f"❌ Erro ao enviar Webhook: {e}")

def send_status_update(message):
    """
    Envia uma atualização de status simples para o Discord.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url: return

    payload = {
        "embeds": [{
            "title": "📡 Radar Status Update",
            "description": message,
            "color": 0x34495e, # Cinza/Azul escuro
            "footer": {"text": "Opportunity Aggregator Monitoring"}
        }]
    }
    try:
        requests.post(webhook_url, json=payload)
    except: pass
