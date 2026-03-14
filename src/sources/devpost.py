import feedparser

def fetch_devpost():
    url = "https://devpost.com/hackathons.rss"
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "url": entry.link,
            "description": entry.summary,
            "source": "Devpost",
            "type": "Hackathon"
        })
    return results
