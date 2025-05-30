from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part

from langchain_together import ChatTogether
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class DistrictAnalysisAgent(BaseAgent):
    llm_model: ChatTogether
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, llm_model: ChatTogether):
        super().__init__(name=name, llm_model=llm_model)
        self.llm_model = llm_model

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        section_name = "Дүүргийн мэдээлэл"
        state = ctx.session.state

        location = state.get("location")
        if not location:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                content=Content(parts=[Part.from_text(text="⚠️ Байршлын мэдээлэл олдсонгүй.")]),
                actions=EventActions(state_delta={}),
                branch=ctx.branch
            )
            return

        try:
            price_info = {
                "Нийт байрны 1м2 дундаж үнэ": {"Хан-Уул": "4,000,323 төгрөг", "Баянгол": "3,510,645 төгрөг"},
                "2 өрөө байрны 1м2 дундаж үнэ": {"Хан-Уул": "4,100,323 төгрөг", "Баянгол": "3,610,645 төгрөг"},
                "3 өрөө байрны 1м2 дундаж үнэ": {"Хан-Уул": "3,900,323 төгрөг", "Баянгол": "3,410,645 төгрөг"},
            }

            prompt_template = """
Байршилийн мэдээлэл өгөгдөх үед харгалзах дүүргийн м2 квадратын дундаж мэдээллүүдийг харуулна уу.

Байршилийн мэдээлэл:
<context>
{context}
</context>

Үнийн мэдээлэл:
<context>
{price_context}
</context>

Your output must strictly follow the following format, (no additional text):
   - Дүүрэг: [Дүүргийн нэр]\n
       - Нийт байрны 1м2 дундаж үнэ: [TO BE FILLED]\n
       - 2 өрөө байрны 1м2 дундаж үнэ: [TO BE FILLED]\n
       - 3 өрөө байрны 1м2 дундаж үнэ: [TO BE FILLED]\n
   - Харьцуулалт: \n [Бусад дүүргүүдийн дундаж үнэтэй харьцуулсан мэдээлэл]\n

Your output:
"""
            prompt = PromptTemplate.from_template(prompt_template)
            chain = prompt | self.llm_model | StrOutputParser()
            response = await chain.ainvoke({
                "context": location,
                "price_context": str(price_info)
            })

            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(state_delta={
                    "analysis_background": [{
                        "section": section_name,
                        "content": response
                    }]
                }),
                content=Content(parts=[Part.from_text(text=response)]),
                branch=ctx.branch
            )

        except Exception as e:
            print("❌ Error:", e)
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=Content(parts=[Part.from_text(text="❌ Алдаа гарлаа: " + str(e))]),
            )
