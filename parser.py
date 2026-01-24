import feedparser

def get_cnn_top_stories():
    # Aqui vai depois os links
    feed_url = "http://rss.cnn.com/rss/cnn_topstories.rss"
    feed = feedparser.parse(feed_url)

    opportunities = []
    for entry in feed.entries:
        opportunities.append({
            "title": entry.title,
            "url": entry.link,
            "description": entry.summary,
                        "source": "CNN"  
                    })
    return opportunities

def limpar_dados(noticia):
    # Pacote com os nomes
    dados_limpos = {
        "titulo": noticia.title,
        "link": noticia.link,
        "descricao": noticia.summary
    }
    return dados_limpos
    primeira_noticia_limpa - limpar_dados(noticias[0])
    print(f"Link da oportunidade {primeira_noticia_limpa['link']}")

if __name__ == "__main__":
    stories = get_cnn_top_stories()
    print(stories)