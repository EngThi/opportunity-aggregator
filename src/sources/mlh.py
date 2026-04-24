import requests
from bs4 import BeautifulSoup
import json
import html

def fetch_mlh():
    url = "https://mlh.io/seasons/2026/events"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "lxml")
        app_div = soup.find("div", id="app")
        if not app_div: return []
        data = json.loads(html.unescape(app_div["data-page"]))

        # MLH uses different keys sometimes like upcomingEvents or upcoming_events
        props = data.get("props", {})
        events = props.get("upcoming_events") or props.get("upcomingEvents") or []

        return [{
            "title": e.get("name"),
            "url": e.get("website_url") or f"https://mlh.io{e.get('url', '')}",
            "description": f"{e.get('dateRange') or e.get('date_range')} - {e.get('location')}",
            "source": "MLH",
            "type": "Hackathon"
        } for e in events]
    except: return []