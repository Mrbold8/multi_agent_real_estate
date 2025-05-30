# multi_agents/agents/writer/simple_writer_agent.py

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
        # 1. Grab merged state from the session
        session_state = ctx.session.state  # type: dict[str, any]
        urls     = session_state.get("urls", [])
        contents = session_state.get("contents", [])
        # If you also used page-scraper, they might have set these:
        title    = session_state.get("title")
        price    = session_state.get("price")
        location = session_state.get("location")
        space    = session_state.get("space")
        # title    = None
        # price    = None
        # location = None
        # space    = None

        # 2. Build summary lines
        lines: list[str] = []
        if title:
            lines.append(f"Property: {title} in {location}, {space} m², priced at {price}.")
        elif urls:
            lines.append("Search results:")
            for u, c in zip(urls, contents):
                lines.append(f"- {u}: {c}")
        else:
            lines.append("No results found for your query.")

        summary = "\n".join(lines)

        # 3. Emit one final Event with content + optional state persistence
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=Content(parts=[Part(text=summary)]),
            actions=EventActions(state_delta={"final_response": summary})
        )
