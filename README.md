# Үл хөдлөх хөрөнгийн туслах

Гүйцэтгэсэн багийн гишүүд: 
- М.Амарболд 21B1NUM0606
- Б.Цолмон 21B1NUM1497
- М.Ариунаа 21B1NUM1719

---

## Хангаж буй шаардлагууд

| Шаардлага | Хангаж буй хэлбэр |
|-----------|-------------------|
| **Vectorstore ашигласан** | FAISS ашиглан заруудыг embeddings болгон хадгалж, төстэй заруудыг хайдаг (`real_estate_crawler_faiss_agent.py`, `faiss_query_agent.py`) |
| **5 бүлэгтэй тайлан** | Тайланд: 1) Товч мэдээлэл, 2) Интернэт хайлт, 3) Unegui.mn зарууд, 4) FAISS хайлт, 5) Дүүргийн дүн шинжилгээ багтдаг |
| **Unegui.mn сайт ашигласан** | BeautifulSoup ашиглан заруудыг татаж, FAISS-д оруулдаг (`real_estate_crawler_faiss_agent.py`) |
| **Интернэт хайлт ашигласан** | Tavily API ашиглан вэб хайлт хийж, агуулгыг PDF-д оруулдаг (`tavily_search_agent.py`) |
| **PDF тайлан гаргадаг** | Unicode-дэмждэг `fpdf` ашиглан тайлан үүсгэдэг (`simple_writer_agent.py`) |
| **Chain-of-Thought reasoning ашигласан** | Байршлын логик тайлбар, харьцуулалт бүхий дүн шинжилгээ (`district_analysis.py`) |

---

## Ашигласан технологиуд

| Технологи | Үүрэг |
|-----------|------|
| **LangChain** | FAISS, Prompt, OutputParser |
| **Google ADK** | Агент бүрдүүлэлт ба удирдлага |
| **FAISS** | Embedding хайлт, төстэй зарууд |
| **Tavily API** | Интернэт хайлт |
| **fpdf** | Unicode PDF тайлан үүсгэх |
| **BeautifulSoup** | Unegui.mn вэбээс HTML scrape хийх |

---

## Агентууд ба үүргүүд

| Агент нэр | Үүрэг |
|-----------|------|
| `DynamicRetrievalAgent` | Хэрэглэгчийн input-оос URL эсвэл текст таньж `PageRetriever` эсвэл `TavilySearch` руу салгаж өгдөг |
| `RealEstateCrawlerAndIndexerAgent` | Unegui.mn сайтаас зарууд татаж, FAISS индекс үүсгэдэг |
| `FaissQueryAgent` | FAISS-д хадгалагдсан заруудаас төстэй хайлт хийдэг |
| `TavilySearchAgent` | Түлхүүр үгсээр вэб хайлт хийж, үр дүнг боловсруулдаг |
| `DistrictAnalysisAgent` | Байршлын мэдээлэлд үндэслэн үнэ, харьцуулалт бүхий дүн шинжилгээ хийдэг |
| `SimpleWriterAgent` | Бүх үр дүнг цуглуулж, тайлан болгон PDF файл үүсгэдэг |

---

## Тайлангийн бүтэц

Тайлан нь дараах 5 хэсэгт хуваагддаг:

1. **Үл хөдлөх хөрөнгийн товч мэдээлэл**
2. **Интернэт хайлтын үр дүн**
3. **Unegui.mn сайтын зарууд**
4. **Ижил төстэй зарууд (FAISS хайлт)**
5. **Дүүргүүдийн дүн шинжилгээ (Chain-of-Thought)**

---

## Ажиллуулах заавар

```bash
pip install -r requirements.txt
```

Төслийг Google ADK Web UI ашиглан ажиллуулна.

```bash
adk web
```