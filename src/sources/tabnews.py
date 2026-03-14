import feedparser

def fetch_tabnews():
    url = "https://www.tabnews.com.br/recentes/rss"
    feed = feedparser.parse(url)
    return [{
        "title": entry.title,
        "url": entry.link,
        "description": "Notícias e oportunidades tech",
        "source": "TabNews",
        "type": "News"
    } for entry in feed.entries[:10]]
