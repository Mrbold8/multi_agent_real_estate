import asyncio

from typing import AsyncGenerator, ClassVar
from typing_extensions import override

from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext

import requests

import os

class TavilySearchAgent(BaseAgent):
    API_URL: ClassVar[str] = "https://api.tavily.com/search"

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        raw_content = ctx.user_content
        query = "".join(p.text for p in raw_content.parts if p.text).strip()

        api_key = os.getenv("TAVILY_API_KEY", "")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "max_results": 8,
            "search_depth": "advanced",
            "chunks_per_source": 3,
            "days": 7,
            "include_answer": True,
            "include_domains": [
                # "www.unegui.mn",
                # "www.osmo.mn",
                # "www.c21.mn",
                # "www.remax.mn",
            ],
            "exclude_domains": [],
        }

        resp = requests.post(self.API_URL, json=payload, headers=headers, timeout=10)
        print(f"[Tavily] HTTP {resp.status_code}, body={resp.text!r}")  # add this
        resp.raise_for_status()
        data = resp.json()
        listings = data.get("results", [])

        urls = []
        contents = []
        for item in listings:
            url = item.get("url")
            snippet = item.get("content", "")
            if url:
                urls.append(url)
                contents.append(snippet)

        yield Event(
            invocation_id=ctx.invocation_id,
            actions=EventActions(state_delta={
                "urls": urls,
                "contents": contents,
            }),
            author=self.name,
            branch=ctx.branch
        )

        await asyncio.sleep(0.1)
