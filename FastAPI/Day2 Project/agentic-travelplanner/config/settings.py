import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENWEATHER_API_KEY"] = os.getenv("OPENWEATHER_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERP_API_KEY"] = os.getenv("SERP_API_KEY")
os.environ["EXCHANGE_RATE_API"] = os.getenv("EXCHANGE_RATE_API")

SERPER_API_KEY = os.environ["SERPER_API_KEY"]
OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
SERP_API_KEY = os.environ["SERP_API_KEY"]
EXCHANGE_RATE_API = os.environ["EXCHANGE_RATE_API"]


def build_llm(model: str = "gpt-4o"):
    """Return ChatOpenAI client (reads openAI from environment)"""
    return ChatOpenAI(model=model , temperature = 0.2)
