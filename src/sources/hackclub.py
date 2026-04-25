import requests
from bs4 import BeautifulSoup
from datetime import datetime

EVENTS_API = "https://events.hackclub.com/api/events/upcoming"
YSWS_URL = "https://ysws.hackclub.com"

# Fallback hardcoded de programas YSWS ativos
YSWS_KNOWN = [
    {"title": "Flavortown", "description": "Ship any project — code, art, game, hardware. Hack Club rewards you.", "url": "https://flavortown.hackclub.com", "category": "Any", "reward": "Hack Club swag", "status": "active"},
    {"title": "Onboard", "description": "Design your first PCB and Hack Club manufactures it for free.", "url": "https://onboard.hackclub.com", "category": "Hardware", "reward": "Free PCB fabrication", "status": "active"},
    {"title": "Sprig", "description": "Build a game using the Sprig engine and receive a physical Sprig console.", "url": "https://sprig.hackclub.com", "category": "Game Dev", "reward": "Sprig handheld console", "status": "active"},
    {"title": "Blot", "description": "Create generative art with code and receive a Blot drawing machine.", "url": "https://blot.hackclub.com", "category": "Art", "reward": "Blot drawing machine kit", "status": "active"},
    {"title": "Swirl", "description": "Build a website/web project and get rewarded.", "url": "https://swirl.hackclub.com", "category": "Web Dev", "reward": "Hack Club swag", "status": "active"},
    {"title": "Hackpad", "description": "Design and build a macropad (mini keyboard) — hardware + firmware.", "url": "https://hackpad.hackclub.com", "category": "Hardware", "reward": "PCB + components", "status": "active"},
]

def fetch_hackclub_events():
    """Consome a API oficial do events.hackclub.com"""
    opps = []
    try:
        data = requests.get(EVENTS_API, timeout=8).json()
        for ev in data[:8]:
            is_ama = ev.get("ama", False)
            category = "AMA" if is_ama else "Event"
            start_raw = ev.get("start", "")
            
            try:
                dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
                date_str = dt.strftime("%b %d, %Y")
            except:
                date_str = start_raw[:10]

            opps.append({
                "title": f"[HC {category}] {ev.get('title', 'Event')}",
                "description": f"{ev.get('desc', '')[:180]} | Leader: {ev.get('leader', 'N/A')} | Date: {date_str}",
                "url": f"https://events.hackclub.com/{ev.get('slug', '')}",
                "source": "Hack Club Events API",
                "type": "event",
                "cal": ev.get("cal"),
                "youtube": ev.get("youtube"),
                "tags": ["hackclub", "event", "ama" if is_ama else "workshop"],
            })
    except Exception as e:
        print(f"⚠️ HC events API failed: {e}")
    return opps

def fetch_hackclub_ysws():
    """Retorna programas YSWS — tenta scrape, usa fallback se falhar"""
    opps = []
    try:
        r = requests.get(YSWS_URL, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("div", class_=lambda c: c and "program" in c.lower())
        for card in cards[:12]:
            title = card.find(["h2", "h3", "strong"])
            desc = card.find("p")
            link = card.find("a", href=True)
            if title:
                opps.append({
                    "title": f"[YSWS] {title.get_text(strip=True)}",
                    "description": desc.get_text(strip=True) if desc else "Build something, get rewarded.",
                    "url": link["href"] if link else YSWS_URL,
                    "source": "Hack Club YSWS",
                    "type": "ysws",
                    "tags": ["hackclub", "ysws"],
                })
    except:
        pass

    if not opps:
        for p in YSWS_KNOWN:
            opps.append({
                "title": f"[YSWS] {p['title']}",
                "description": f"{p['description']} | Category: {p['category']} | Reward: {p['reward']}",
                "url": p["url"],
                "source": "Hack Club YSWS",
                "type": "ysws",
            })
    return opps

def fetch_hackclub():
    results = []
    results.extend(fetch_hackclub_ysws())
    results.extend(fetch_hackclub_events())
    return results
