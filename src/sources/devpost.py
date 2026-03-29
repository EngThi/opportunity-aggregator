import requests
import re
from datetime import datetime

DEVPOST_API = "https://devpost.com/api/hackathons"

def clean_html(text):
    if not text: return ""
    return re.sub(r'<[^>]*>', '', text)

def fetch_devpost():
    """
    Fetches upcoming hackathons from Devpost API.
    """
    opportunities = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    try:
        response = requests.get(DEVPOST_API, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("hackathons", [])[:20]:
                prize = clean_html(item.get('prize_amount', 'N/A'))
                opportunities.append({
                    "title": item.get("title", "No title"),
                    "url": item.get("url", ""),
                    "description": f"Prize: {prize} | {item.get('time_left_to_submission', '')}",
                    "source": "Devpost",
                    "type": "Hackathon"
                })
            print(f"✅ Devpost: {len(opportunities)} hackathons found via API.")
        else:
            print(f"⚠️ Devpost API returned status code {response.status_code}")
    except Exception as e:
        print(f"⚠️ Devpost fetch failed: {e}")
    return opportunities

