import requests

def fetch_github_jobs():
    # Busca simplificada usando a API de busca do GitHub por issues abertas com label "job" ou "vaga"
    url = "https://api.github.com/search/issues?q=label:job+is:open+state:open&sort=created&order=desc"
    try:
        response = requests.get(url, timeout=10)
        items = response.json().get("items", [])
        return [{
            "title": i.get("title"),
            "url": i.get("html_url"),
            "description": i.get("body", "")[:200],
            "source": "GitHub Jobs",
            "type": "Job"
        } for i in items[:10]]
    except: return []
