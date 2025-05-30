from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.adk.agents.invocation_context import InvocationContext

import requests
from bs4 import BeautifulSoup
import time
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from pydantic import PrivateAttr

BASE_URL = "https://www.unegui.mn"
LISTING_URL = f"{BASE_URL}/l-hdlh/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def findFeature(li_list, header):
    for li in li_list:
        text = li.text.strip()
        if text.startswith(header):
            return text[len(header) + 1:]
    return "NA"

def extract_listing_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("h1", {"class": "title-announcement"})
        price = soup.find("div", {"class": "announcement-price__cost"})
        location = soup.find("span", {"itemprop": "address"})
        li_class = soup.find_all("li")

        return {
            "url": url,
            "title": title.text.strip() if title else "N/A",
            "price": price.text.strip() if price else "N/A",
            "location": location.text.strip() if location else "N/A",
            "space": findFeature(li_class, 'Талбай:')
        }
    except Exception as e:
        print("❌ Error parsing", url, e)
        return None

class RealEstateCrawlerAndIndexerAgent(BaseAgent):
    _max_pages: int = PrivateAttr()
    _embedding_model: HuggingFaceEmbeddings = PrivateAttr()

    def __init__(self, name: str, max_pages: int = 3):
        super().__init__(name=name)
        self._max_pages = max_pages
        self._embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    @property
    def embedding_model(self):
        return self._embedding_model

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        listings = []
        for page in range(1, self._max_pages + 1):
            paged_url = f"{LISTING_URL}?page={page}"
            response = requests.get(paged_url, headers=HEADERS)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.select("a[href^='/adv/']")
            unique_urls = list(set(BASE_URL + link['href'] for link in links))

            for url in unique_urls[:10]:  # crawl only first 10 per page for speed
                data = extract_listing_data(url)
                if data:
                    listings.append(data)
                time.sleep(1.0)  # prevent being blocked

        docs = []
        for item in listings:
            content = f"Title: {item['title']}\nLocation: {item['location']}\nPrice: {item['price']}\nSpace: {item['space']}\nURL: {item['url']}"
            docs.append(Document(page_content=content, metadata={"source": item["url"]}))

        vectorstore = FAISS.from_documents(docs, self.embedding_model)
        vectorstore.save_local("faiss_index")

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=Content(parts=[Part(text=f"✅ Crawled {len(listings)} listings and indexed to FAISS.")]),
            actions=EventActions(state_delta={
                "crawled_listings": listings,
                "faiss_index_created": True
            })
        )
