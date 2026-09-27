from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
)


def get_embeddings():
    """
    Create and return the Gemini embedding model.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY,
    )

    return embeddings
