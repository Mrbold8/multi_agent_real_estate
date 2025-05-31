import logging
from typing import AsyncGenerator, Sequence
from typing_extensions import override
import copy
import json
import os, sys
import re
import urllib.parse

from google.adk.agents import (
    LlmAgent, BaseAgent, LoopAgent, SequentialAgent, ParallelAgent
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, HttpOptions, Part
from google import genai

from langchain_core.documents import Document
from langchain_together import ChatTogether

from multi_agents.agents.retrieval.real_estate_page_agent import RealEstatePageRetriever
from multi_agents.agents.retrieval.dynamic_retrieval_agent import DynamicRetrievalAgent
from multi_agents.agents.retrieval.real_estate_crawler_faiss_agent import RealEstateCrawlerAndIndexerAgent
from multi_agents.agents.retrieval.faiss_query_agent import FaissQueryAgent
from multi_agents.agents.research.district_analysis import DistrictAnalysisAgent
from multi_agents.agents.write.simple_writer_agent import SimpleWriterAgent

os.environ["OTEL_SDK_DISABLED"] = "true"
logging.getLogger("opentelemetry").setLevel(logging.CRITICAL)

# --- Model ---
LLM_Model = "gemini-1.5-pro"

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Instantiate LLM ---
llm = ChatTogether(
    together_api_key="abeb6dac65702ac49f10790d3182b32707afa1d9fe64eea4bb88fffdc7051049",
    model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
)

# --- Agents ---
page_retriever = RealEstatePageRetriever(name="page_retriever")
retriever = DynamicRetrievalAgent(name="dynamic_retrieval")
crawler_faiss = RealEstateCrawlerAndIndexerAgent(name="crawler_and_indexer")
faiss_query = FaissQueryAgent(name="faiss_query")
district_analysis = DistrictAnalysisAgent(name="district_analysis", llm_model=llm)
writer = SimpleWriterAgent(name="simple_writer")

# --- Workflows ---

# Retrieval pipeline
parallel_retrieval_agent = ParallelAgent(
    name="ParallelRetrievalSubworkflow",
    sub_agents=[
        retriever,
        crawler_faiss,
        faiss_query
    ]
)

# Analysis pipeline
parallel_analysis_agent = ParallelAgent(
    name="ParallelAnalysisSubWorkflow",
    sub_agents=[district_analysis]
)

# Main Workflow
root_agent = SequentialAgent(
    name="real_estate_workflow",
    sub_agents=[
        page_retriever,
        parallel_retrieval_agent,
        parallel_analysis_agent,
        writer  
    ]
)
