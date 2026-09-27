import os

from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# Gemini models
LLM_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-001"


# ChromaDB configuration
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "financial_report_2025"

# Number of documents to retrieve for RAG
RETRIEVAL_K = 3
