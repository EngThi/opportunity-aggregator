import feedparser
from datetime import datetime

DEVPOST_RSS = "https://devpost.com/hackathons.rss"

def fetch_devpost():
    """
    Fetches upcoming hackathons from Devpost RSS feed.
    """
    opportunities = []
    try:
        feed = feedparser.parse(DEVPOST_RSS)
        for entry in feed.entries[:20]:
            opportunities.append({
                "title": entry.get("title", "No title"),
                "url": entry.get("link", ""),
                "description": entry.get("summary", "")[:300],
                "source": "Devpost",
                "type": "Hackathon"
            })
        print(f"✅ Devpost: {len(opportunities)} hackathons found.")
    except Exception as e:
        print(f"⚠️ Devpost fetch failed: {e}")
    return opportunities
