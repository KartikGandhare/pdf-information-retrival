from langchain_chroma import Chroma

from app.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
)

from app.ingestion.embeddings import get_embeddings


def get_vectorstore():
    """
    Connect to the existing ChromaDB collection.
    """

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )

    return vectorstore
