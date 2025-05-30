from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.adk.agents.invocation_context import InvocationContext

from fpdf import FPDF
import textwrap
import re
import os
import asyncio

# Escape тэмдэгтүүдийг арилгах
def strip_invisible(text: str) -> str:
    return re.sub(r'\x1b[^m]*m', '', text)

# Урт тасралтгүй string-ийг PDF-ийн өргөнд багтаахаар хуваах
def force_break_long_line(text: str, max_width: float, pdf: FPDF):
    result = []
    buffer = ""
    for char in text:
        if pdf.get_string_width(buffer + char) <= max_width:
            buffer += char
        else:
            if buffer:
                result.append(buffer)
            buffer = char
    if buffer:
        result.append(buffer)
    return result

# Unicode дэмждэг PDF writer
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font("Noto", "", "./fonts/NotoSans-Regular.ttf", uni=True)
        self.set_font("Noto", "", 12)

    def write_title(self, text: str):
        self.set_font("Noto", "", 14)
        self.set_text_color(*hex_to_rgb("#347786"))
        self.ln(5)
        self.cell(0, 10, txt=text, ln=True)
        self.set_text_color(0, 0, 0)
        self.set_font("Noto", "", 12)

    def write_bullet(self, text: str, color=(0, 0, 0)):
        max_width = self.w - 2 * self.l_margin
        line_height = 8
        wrapped = force_break_long_line(text, max_width - 5, self)

        self.set_text_color(*color)
        for i, line in enumerate(wrapped):
            bullet = "\u2022 " if i == 0 else "   "
            self.cell(0, line_height, bullet + line, ln=True)
        self.set_text_color(0, 0, 0)

# SimpleWriterAgent
class SimpleWriterAgent(BaseAgent):
    def save_summary_to_pdf(self, sections: list[tuple[str, list[str]]], filename: str = "report.pdf"):
        pdf = UnicodePDF()
        for title, lines in sections:
            pdf.write_title(title)

            if "FAISS" in title:
                color = (85, 85, 85)
            elif "Дүүргийн дүн шинжилгээ" in title:
                color = (88, 88, 88)
            else:
                color = (0, 0, 0)

            for line in lines:
                pdf.write_bullet(line, color=color)

        # PDF-г прожектын root д хадгалах
        full_path = os.path.abspath(filename)
        pdf.output(full_path)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state

        urls     = state.get("urls", [])
        contents = state.get("contents", [])
        title    = state.get("title")
        price    = state.get("price")
        location = state.get("location")
        space    = state.get("space")
        listings = state.get("crawled_listings", [])
        faiss_answer = state.get("faiss_answer")
        analysis_background = state.get("analysis_background", [])

        sections: list[tuple[str, list[str]]] = []

        # 1. Үл хөдлөх хөрөнгийн товч мэдээлэл
        overview_lines = []
        if title:
            overview_lines.append(f"'{title}' байршил: {location}, хэмжээ: {space} м², үнэ: {price}.")
        else:
            overview_lines.append("Үл хөдлөх мэдээлэл байхгүй.")
        sections.append(("1) Үл хөдлөх хөрөнгийн товч мэдээлэл", overview_lines))

        # 2. Интернэт хайлтын үр дүн
        search_lines = []
        if urls and contents:
            for u, c in zip(urls, contents):
                search_lines.append(f"{u}: {c}")
        else:
            search_lines.append("Интернэтээс үр дүн олдсонгүй.")
        sections.append(("2) Интернэт хайлтын үр дүн", search_lines))

        # 3. Unegui.mn сайтын зарууд
        listing_lines = []
        if listings:
            listing_lines.append(f"Нийт {len(listings)} зар байна.")
            for i, item in enumerate(listings[:5]):
                listing_lines.append(
                    f"{i+1}. {item['title']} - {item['location']}, {item['space']} м², {item['price']}"
                )
        else:
            listing_lines.append("Unegui.mn сайтаас зар олдсонгүй.")
        sections.append(("3) Unegui.mn сайтын зарууд", listing_lines))

        # 4. Ижил төстэй зарууд
        faiss_lines = []
        if faiss_answer:
            faiss_lines.append(faiss_answer)
        else:
            faiss_lines.append("Ижил төстэй зарууд байхгүй.")
        sections.append(("4) Ижил төстэй зарууд", faiss_lines))

        # 5. Дүүргүүдийн дүн шинжилгээ
        analysis_lines = []
        if analysis_background:
            for section in analysis_background:
                analysis_lines.append(f"{section['section']}: {section['content']}")
        else:
            analysis_lines.append("Дүүргүүдийн дүн шинжилгээ байхгүй.")
        sections.append(("5) Дүүргүүдийн дүн шинжилгээ", analysis_lines))

        # Generate PDF in static folder
        pdf_filename = "report.pdf"
        self.save_summary_to_pdf(sections, filename=pdf_filename)

        # ADK Web UI-д харуулах линк (локал server static serve хийдэг)
        file = "PDF тайлан прожект дотор хадгалагдсан. Очиж үзнэ үү."

        full_output = "\n\n".join([f"{s[0]}\n" + "\n".join(s[1]) for s in sections]) + "\n\n" + file

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=Content(parts=[Part(text=full_output)]),
            actions=EventActions(state_delta={"final_response": full_output})
        )
