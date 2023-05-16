from typing import Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd
import requests
import concurrent.futures


class WebScraper:
    def __init__(self, url):
        self.url: str = url
        self.data: List[Dict[str, str]] = []

    def get_page(self, page_num):
        try:
            url = f"{self.url}/page/{page_num}/"
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None

        page = response.content
        soup = BeautifulSoup(page, "html.parser")
        return soup

    def scrape_page(self, page_num):
        print(f"Extracting data from page {page_num}...")
        soup = self.get_page(page_num)

        if soup is None:
            print("Error: Failed to fetch page")
            return None

        tools = soup.find_all("article", {"class": "post-card"})

        for tool in tools:
            name: str = tool.find(
                "h2", {"class": "post-card-title"}).text.strip()
            tags = tool.find_all(
                "span", {"class": "post-card-primary-tag"})
            types = ", ".join([tag.text.strip() for tag in tags])
            image_url = tool.find(
                "img", {"class": "post-card-image"})["src"]
            if not urlparse(image_url).scheme:
                image_url = urljoin(self.url, image_url)
            url: str = urljoin(self.url, tool.find("a",
                                                   {"class": "post-card-image-link"})["href"])
            description: str = tool.find(
                "div", {"class": "post-card-excerpt"}).text.strip()

            self.data.append({
                "name": name,
                "type": types,
                "image": image_url,
                "url": url,
                "description": description
            })

        print(f"Data extracted from page {page_num}.")

    def scrape_pages(self, start_page, end_page):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for page_num in range(start_page, end_page + 1):
                futures.append(executor.submit(self.scrape_page, page_num))

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    print(f"Error: {future.exception()}")

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


scraper = WebScraper("https://gpte.ai")
scraper.scrape_pages(1, 80)
scraper.save_to_excel("gpte-data.xlsx")
