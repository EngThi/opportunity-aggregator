import requests
from bs4 import BeautifulSoup
import json
import html

def fetch_mlh():
    url = "https://mlh.io/events"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # O MLH guarda os dados em um atributo data-page de uma div #app
        app_div = soup.find("div", id="app")
        if not app_div: return []
        
        data = json.loads(html.unescape(app_div["data-page"]))
        props = data.get("props", {})
        events = props.get("upcoming_events") or props.get("upcomingEvents") or []
        
        results = []
        for e in events:
            # Garante que a URL seja válida
            raw_url = e.get("website_url") or e.get("url") or ""
            if raw_url.startswith("/"):
                final_url = f"https://mlh.io{raw_url}"
            else:
                final_url = raw_url
            
            # Limpeza: Alguns links do MLH vêm com /prizes no final mas a página principal é melhor
            if "/prizes" in final_url:
                final_url = final_url.split("/prizes")[0]

            results.append({
                "title": e.get("name"),
                "url": final_url,
                "description": f"{e.get('dateRange') or e.get('date_range')} - {e.get('location')}",
                "source": "MLH",
                "type": "Hackathon"
            })
        return results
    except Exception as e:
        print(f"⚠️ Erro MLH: {e}")
        return []
