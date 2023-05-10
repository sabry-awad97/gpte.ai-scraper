from typing import Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd
import requests


class WebScraper:
    def __init__(self, url, page_num=1):
        self.url: str = url
        self.page_num: int = page_num
        self.page: bytes | None = None
        self.soup: BeautifulSoup | None = None
        self.data: List[Dict[str, str]] = []

    def get_page(self):
        try:
            url = f"{self.url}/page/{self.page_num}/"
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None

        self.page = response.content
        self.soup = BeautifulSoup(self.page, "html.parser")
        return self.soup
