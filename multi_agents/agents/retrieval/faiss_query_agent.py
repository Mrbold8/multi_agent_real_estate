from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import re

class FaissQueryAgent(BaseAgent):
    def __init__(self, name: str, index_path: str = "faiss_index"):
        super().__init__(name=name)
        self._embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self._index_path = index_path
        try:
            self._vectorstore = FAISS.load_local(
                "faiss_index",
                self._embedding_model,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            self._vectorstore = None
            self._load_error = str(e)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        query = "".join(p.text for p in ctx.user_content.parts if p.text).strip()

        if not query:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=Content(parts=[Part(text="Хайлтын query олдсонгүй.")])
            )
            return

        if not self._vectorstore:
            error_message = f"FAISS индекс ачаалагдаагүй байна. Алдаа: {getattr(self, '_load_error', 'Тодорхойгүй')}"
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=Content(parts=[Part(text=error_message)])
            )
            return

        results = self._vectorstore.similarity_search(query, k=5)

        if not results:
            answer = "Тохирох үл хөдлөх хөрөнгийн мэдээлэл олдсонгүй."
            state_delta = {}
        else:
            answer = "Тохирох зарууд:\n\n" + "\n\n".join(
                f"{i + 1}. {doc.page_content}" for i, doc in enumerate(results)
            )

            # Байршлын мэдээллийг үр дүнгээс задлах
            match = re.search(r"Location:\s*(.*)", results[0].page_content)
            location = match.group(1).strip() if match else None

            state_delta = {"faiss_answer": answer}
            if location:
                state_delta["location"] = location

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=Content(parts=[]),
            actions=EventActions(state_delta=state_delta)
        )
