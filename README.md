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
| **5 бүлэгтэй тайлан** | Тайланд: 1) Хэрэглэгчийн асуултад суурилсан хөрөнгийн мэдээлэл, 2) Интернэт хайлт, 3) Unegui.mn зарууд, 4) FAISS хайлт, 5) Дүүргүүдийн дүн шинжилгээ багтсан |
| **Unegui.mn сайт ашигласан** | BeautifulSoup ашиглан заруудыг татаж, FAISS-д оруулдаг (`real_estate_crawler_faiss_agent.py`) |
| **Интернэт хайлт ашигласан** | Tavily API ашиглан интернэт хайлт хийж, агуулгыг PDF-д оруулдаг (`tavily_search_agent.py`) |
| **Dynamic Retrieval Agent нэмсэн** | Асуулт эсвэл URL оруулахад тохирох retrieval agent -руу чиглүүлнэ (`dynamic_retrieval_agent.py`) |
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
| **BeautifulSoup** | Unegui.mn сайтаас HTML scrape хийх |

---

## Агентууд ба үүргүүд

| Агент нэр | Үүрэг |
|-----------|------|
| `DynamicRetrievalAgent` | Хэрэглэгчийн input -ээс URL эсвэл текст таньж `PageRetriever` эсвэл `TavilySearch` руу салгаж өгдөг |
| `RealEstateCrawlerAndIndexerAgent` | Unegui.mn сайтаас зарууд татаж, FAISS индекс үүсгэдэг |
| `FaissQueryAgent` | FAISS-д хадгалагдсан заруудаас төстэй заруудыг хайдаг |
| `TavilySearchAgent` | Түлхүүр үгсээр интернэт хайлт хийж, үр дүнг боловсруулдаг. Жишээ нь `Хан уул дүүрэгт 2 өрөө байр` |
| `DistrictAnalysisAgent` | Байршлын мэдээлэлд үндэслэн үнэ, харьцуулалт бүхий дүн шинжилгээ хийдэг |
| `SimpleWriterAgent` | Бүх үр дүнг цуглуулж, тайлан болгон PDF файл үүсгэдэг |

---

## Тайлангийн бүтэц

Тайлан нь дараах 5 хэсэгт хуваагддаг:

1. **Хэрэглэгчийн асуултад суурилсан хөрөнгийн мэдээлэл**
2. **Интернэт хайлтын үр дүн**
3. **Unegui.mn сайтын зарууд**
4. **Ижил төстэй зарууд (FAISS хайлт)**
5. **Дүүргүүдийн дүн шинжилгээ (Chain-of-Thought)**

---

## Ажиллуулах заавар

```bash
python -m venv venv
```

```bash
venv\Scripts\activate 
```

```bash
pip install -r requirements.txt
```

Төслийг Google ADK Web UI ашиглан ажиллуулна.

```bash
adk web
```

## Жишээ асуулт 

- Хан-Уул дүүрэгт 2 өрөө байр хэдэн төгрөг байна?
- https://www.unegui.mn/adv/9381898_5-shard-00-toot-kholsluulne/
