from typing import AsyncGenerator, ClassVar, Pattern
from typing_extensions import override
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext

from multi_agents.agents.retrieval.real_estate_page_agent import RealEstatePageRetriever
from multi_agents.agents.retrieval.tavily_search_agent import TavilySearchAgent

import re

class DynamicRetrievalAgent(BaseAgent):
    URL_REGEX: ClassVar[Pattern] = re.compile(r"^https?://", re.IGNORECASE)

    _page_agent: RealEstatePageRetriever = PrivateAttr()
    _search_agent: TavilySearchAgent = PrivateAttr()

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self._page_agent = RealEstatePageRetriever(name="page_retriever")
        self._search_agent = TavilySearchAgent(name="tavily_search")

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        raw_content = ctx.user_content
        text_parts  = [part.text for part in raw_content.parts if part.text is not None]
        user_input  = "".join(text_parts).strip()
        
        if self.URL_REGEX.match(user_input):
            print("[dynamic] → page_retriever branch")
            async for ev in self._page_agent.run_async(ctx):
                yield ev
        else:
            print("[dynamic] → tavily_search branch")
            async for ev in self._search_agent.run_async(ctx):
                yield ev
