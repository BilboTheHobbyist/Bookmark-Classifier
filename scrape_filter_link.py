# scrape_filter_link.py
import requests
from bs4 import BeautifulSoup

class LinkScraper:
    def __init__(self, url):
        self.url = url
        self.title = ""
        self.description = ""

    def scrape(self):
        try:
            r = requests.get(self.url, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                self.title = soup.title.string.strip() if soup.title else ""
                desc_tag = soup.find("meta", attrs={"name": "description"})
                self.description = desc_tag["content"].strip() if desc_tag else ""
        except Exception as e:
            print(f"Error scraping {self.url}: {e}")
        return self.title, self.description
