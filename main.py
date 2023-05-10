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
