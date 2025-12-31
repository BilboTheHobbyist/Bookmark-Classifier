# scrape_filter_link.py
import requests
from bs4 import BeautifulSoup
from newspaper import Article

class LinkScraper:
    def __init__(self, url, timeout=7):
        self.url = url
        self.timeout = timeout

    def scrape(self):
        data = {
            "title": "",
            "description": "",
            "keywords": [],
            "content": ""
        }

        # --------------------------
        # Basic HTML scraping
        # --------------------------
        try:
            r = requests.get(self.url, timeout=self.timeout, headers={
                "User-Agent": "Mozilla/5.0"
            })
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")

                # Title
                if soup.title and soup.title.string:
                    data["title"] = soup.title.string.strip()

                # Meta description
                desc = soup.find("meta", attrs={"name": "description"})
                if desc and desc.get("content"):
                    data["description"] = desc["content"].strip()

                # Meta keywords
                keys = soup.find("meta", attrs={"name": "keywords"})
                if keys and keys.get("content"):
                    data["keywords"] = [
                        k.strip() for k in keys["content"].split(",") if k.strip()
                    ]
        except Exception:
            pass  # fail silently

        # --------------------------
        # Content scraping (newspaper)
        # --------------------------
        try:
            article = Article(self.url)
            article.download()
            article.parse()
            data["content"] = article.text.strip()
        except Exception:
            # Scraping not allowed or failed
            data["content"] = ""

        return data
