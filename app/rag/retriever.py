from app.config import RETRIEVAL_K
from app.rag.vectorstore import get_vectorstore


def get_retriever():
    """
    Create a retriever from the ChromaDB vector store.
    """

    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": RETRIEVAL_K
        }
    )

    return retriever
