from typing import AsyncGenerator, Sequence
from typing_extensions import override

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.genai import types

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

import requests
import logging
import copy
import json

import urllib.request

from bs4 import BeautifulSoup

def findFeature(li_list, header):
    ret = 'NA'
    for li in li_list:
        text = li.text.strip()
        if text.startswith(header):
            return text[len(header) + 1:]
    return ret

class RealEstatePageRetriever(BaseAgent):
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str):
        super().__init__(name=name)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        url_text = ctx.session.events[0].content.parts[0].text
        url = url_text.strip()

        print("Fetched URL:", url)

        response = None
        try:
            response = requests.get(url, timeout=10)
        except Exception as e:
            print("Request error:", e)

        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            title_tag = soup.find("h1", {"class": "title-announcement"})
            title = title_tag.text.strip() if title_tag else "N/A"

            price_tag = soup.find("div", {"class": "announcement-price__cost"})
            price = price_tag.text.replace('үнэ тохирно', '').strip() if price_tag else "N/A"

            location_tag = soup.find("span", {"itemprop": "address"})
            location = location_tag.text.strip() if location_tag else "N/A"

            li_class = soup.find_all("li")
            space = findFeature(li_class, 'Талбай:')

            print("title:", title)
            print("price:", price)
            print("location:", location)
            print("space:", space)

            yield Event(
                invocation_id=ctx.invocation_id,
                actions=EventActions(state_delta={
                    "title": title,
                    "price": price,
                    "location": location,
                    "space": space
                }),
                content=Content(parts=[]),
                author=self.name,
                branch=ctx.branch
            )
        else:
            print(f"Invalid response or status code for URL: {url}")
            yield Event(
                invocation_id=ctx.invocation_id,
                content=Content(parts=[]),
                author=self.name,
                branch=ctx.branch
            )