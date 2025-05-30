from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.adk.agents.invocation_context import InvocationContext

class SimpleWriterAgent(BaseAgent):
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # --- 1. Session state-ийг авах ---
        state = ctx.session.state  # type: dict[str, any]

        urls     = state.get("urls", [])
        contents = state.get("contents", [])
        title    = state.get("title")
        price    = state.get("price")
        location = state.get("location")
        space    = state.get("space")
        listings = state.get("crawled_listings", [])  # crawler-аас ирсэн мэдээлэл
        faiss_answer = state.get("faiss_answer")       # FAISS хайлтын үр дүн

        # --- 2. Хураангуй текст үүсгэх ---
        lines: list[str] = []

        # 2.1 Хэрэв нэг URL-н дэлгэрэнгүй мэдээлэл байвал
        if title:
            lines.append(f"Property: {title} in {location}, {space} m², priced at {price}.")

        # 2.2 Tavily хайлтын үр дүн байвал
        elif urls and contents:
            lines.append("🔍 Search results from the internet:")
            for u, c in zip(urls, contents):
                lines.append(f"- {u}: {c}")

        # 2.3 Unegui crawler үр дүн байвал
        elif listings:
            lines.append(f"🏠 {len(listings)} listings from Unegui.mn:")
            for i, item in enumerate(listings[:5]):  # эхний 5-г харуулна
                lines.append(
                    f"{i+1}. {item['title']} in {item['location']}, {item['space']} m², {item['price']}₮"
                )

        # 2.4 FAISS хариу байвал
        if faiss_answer:
            lines.append("\n📦 FAISS Similar Search Result:")
            lines.append(faiss_answer)

        # 2.5 Хэрэв юу ч байхгүй бол
        if not lines:
            lines.append("No data found from any agent.")

        # --- 3. Эцсийн event үүсгэх ---
        summary = "\n".join(lines)

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=Content(parts=[Part(text=summary)]),
            actions=EventActions(state_delta={"final_response": summary})
        )
