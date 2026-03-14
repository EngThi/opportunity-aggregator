import requests
from bs4 import BeautifulSoup
import feedparser
import json
import html

def get_devpost_hackathons():
    """
    Scrapes upcoming hackathons from Devpost API.
    """
    url = "https://devpost.com/api/hackathons"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Devpost API error: {response.status_code}")
            return []
        
        data = response.json()
        hackathons = []
        
        for item in data.get("hackathons", []):
            hackathons.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "description": item.get("time_left_to_submission", "N/A"),
                "prize": item.get("prize_amount", "N/A"),
                "source": "Devpost",
                "type": "Hackathon"
            })
        return hackathons
    except Exception as e:
        print(f"Error scraping Devpost API: {e}")
        return []

def get_mlh_opportunities():
    """
    Scrapes hackathons from MLH by parsing the embedded JSON data.
    """
    url = "https://mlh.io/seasons/2026/events"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "lxml")
        
        app_div = soup.find("div", id="app")
        if not app_div or not app_div.has_attr("data-page"):
            print("MLH: Could not find app data div")
            return []
        
        data_str = app_div["data-page"]
        # The data is HTML entities encoded JSON
        data = json.loads(html.unescape(data_str))
        
        events = data.get("props", {}).get("upcoming_events", [])
        opportunities = []
        
        for event in events:
            # MLH URLs in JSON are often relative
            event_url = event.get("website_url") or f"https://mlh.io{event.get('url')}"
            opportunities.append({
                "title": event.get("name"),
                "url": event_url,
                "description": f"{event.get('date_range')} - {event.get('location')}",
                "source": "MLH",
                "type": "Hackathon"
            })
        return opportunities
    except Exception as e:
        print(f"Error scraping MLH: {e}")
        return []

def get_tech_news():
    feed_url = "https://www.tabnews.com.br/recentes/rss"
    feed = feedparser.parse(feed_url)
    news_list = []
    for entry in feed.entries[:5]:
        news_list.append({
            "title": entry.title,
            "url": entry.link,
            "source": "TabNews",
            "type": "News"
        })
    return news_list

if __name__ == "__main__":
    print("Testing Devpost API...")
    devpost = get_devpost_hackathons()
    print(f"Found {len(devpost)} hackathons on Devpost.")
    if devpost:
        print(f"Sample: {devpost[0]['title']} ({devpost[0]['url']})")
    
    print("\nTesting MLH JSON parse...")
    mlh = get_mlh_opportunities()
    print(f"Found {len(mlh)} events on MLH.")
    if mlh:
        print(f"Sample: {mlh[0]['title']} ({mlh[0]['url']})")

    print("\nTesting Tech News...")
    news = get_tech_news()
    print(f"Found {len(news)} news items.")
