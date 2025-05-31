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
                "Нийт байрны 1м2 дундаж үнэ": {
                    "Хан-Уул": "4,000,323 төгрөг",
                    "Баянгол": "3,510,645 төгрөг",
                    "Сүхбаатар": "4,200,000 төгрөг",
                    "Баянзүрх": "3,300,000 төгрөг",
                    "Сонгинохайрхан": "2,950,000 төгрөг",
                    "Чингэлтэй": "3,700,000 төгрөг"
                },
                "2 өрөө байрны 1м2 дундаж үнэ": {
                    "Хан-Уул": "4,100,323 төгрөг",
                    "Баянгол": "3,610,645 төгрөг",
                    "Сүхбаатар": "4,350,000 төгрөг",
                    "Баянзүрх": "3,450,000 төгрөг",
                    "Сонгинохайрхан": "3,000,000 төгрөг",
                    "Чингэлтэй": "3,850,000 төгрөг"
                },
                "3 өрөө байрны 1м2 дундаж үнэ": {
                    "Хан-Уул": "3,900,323 төгрөг",
                    "Баянгол": "3,410,645 төгрөг",
                    "Сүхбаатар": "4,100,000 төгрөг",
                    "Баянзүрх": "3,150,000 төгрөг",
                    "Сонгинохайрхан": "2,850,000 төгрөг",
                    "Чингэлтэй": "3,600,000 төгрөг"
                }
            }


            prompt_template = """
Та үл хөдлөх хөрөнгийн байршил болон м² үнийн мэдээлэл дээр үндэслэн дараах шат дараалсан алхмуудыг хийж логиктой тайлбар өгнө үү:

Алхам 1: Байршлын өгөгдлөөс аль дүүрэгт хамаарахыг тодорхойл.
Алхам 2: price_context доторх тухайн дүүргийн 1м² дундаж үнийг нийт, 2 өрөө, 3 өрөө байраар ангилж харуул.
Алхам 3: Үнийн түвшинг бусад дүүргүүдтэй харьцуулан тайлбарлана уу.

Байршил:
<context>
{context}
</context>

Үнийн мэдээлэл:
<context>
{price_context}
</context>

Зөвхөн доорх форматтай тайлбар буцаа:

   - Дүүрэг: [Дүүргийн нэр]
       - Нийт байрны 1м² дундаж үнэ: [үнэ]
       - 2 өрөө байрны 1м² дундаж үнэ: [үнэ]
       - 3 өрөө байрны 1м² дундаж үнэ: [үнэ]
   - Харьцуулалт:
     [Бусад дүүргүүдтэй харьцуулсан логик дүгнэлт]

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
                content=Content(parts=[]),
                branch=ctx.branch
            )

        except Exception as e:
            print("Error:", e)
