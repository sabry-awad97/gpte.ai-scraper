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

    def extract_data(self):
        print(f"Extracting data from {self.url}...")
        while True:
            if self.soup is None:
                self.get_page()

            if self.soup is None:
                print("Error: Failed to fetch page")
                return None

            posts = self.soup.find_all("article", {"class": "post-card"})

            for post in posts:
                name: str = post.find(
                    "h2", {"class": "post-card-title"}).text.strip()
                tags = post.find_all(
                    "span", {"class": "post-card-primary-tag"})
                types = ", ".join([tag.text.strip() for tag in tags])
                image_url = post.find(
                    "img", {"class": "post-card-image"})["src"]
                if not urlparse(image_url).scheme:
                    image_url = urljoin(self.url, image_url)
                url: str = urljoin(self.url, post.find("a",
                                                       {"class": "post-card-image-link"})["href"])
                description: str = post.find(
                    "div", {"class": "post-card-excerpt"}).text.strip()

                self.data.append({
                    "name": name,
                    "type": types,
                    "image": image_url,
                    "url": url,
                    "description": description
                })

            print(f"Data extracted from page {self.page_num}.")

            self.page_num += 1
            self.soup = None
            if not self.get_page():
                break

        print("Data extraction complete!")

    def save_to_excel(self, file_name):
        print("Saving data to Excel...")
        if not file_name.endswith(".xlsx"):
            file_name += ".xlsx"

        try:
            df = pd.DataFrame(self.data)
            df.to_excel(file_name, index=False)
            print(f"Data saved to {file_name} successfully!")
        except Exception as e:
            print(f"Error: {e}")
            return None
