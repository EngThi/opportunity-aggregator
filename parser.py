import feedparser

def get_tech_news():
    """
    Fetches the latest tech news from TabNews RSS feed.
    Returns a list of dictionaries with title, url, and source.
    """
    feed_url = "https://www.tabnews.com.br/recentes/rss"
    feed = feedparser.parse(feed_url)

    news_list = []
    
    # Let's get the top 5 entries to keep it clean for now
    for entry in feed.entries[:5]:
        news_list.append({
            "title": entry.title,
            "url": entry.link,
            "source": "TabNews"
        })
    
    return news_list

if __name__ == "__main__":
    # Test the parser when running this file directly
    print("Fetching news from TabNews...")
    news = get_tech_news()
    for item in news:
        print(f"- {item['title']} ({item['url']})")