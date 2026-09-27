import hashlib
from pathlib import Path

from app.ingestion.loader import load_pdf
from app.ingestion.chunker import split_text
from app.rag.vectorstore import get_vectorstore


def create_document_id(file_path: str) -> str:
    """
    Create a unique ID based on the PDF file contents.
    """

    pdf_path = Path(file_path)

    file_bytes = pdf_path.read_bytes()

    return hashlib.sha256(file_bytes).hexdigest()


def ingest_pdf(file_path: str):
    """
    Read a PDF, split its text into chunks,
    and store the chunks in ChromaDB.

    If the exact same PDF was already ingested,
    it will not be added again.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    # Step 1: Create a unique ID for this PDF
    document_id = create_document_id(file_path)

    # Step 2: Extract text
    text = load_pdf(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from the PDF."
        )

    # Step 3: Split text into chunks
    chunks = split_text(text)

    if not chunks:
        raise ValueError(
            "No chunks were created from the PDF."
        )

    # Step 4: Connect to ChromaDB
    vectorstore = get_vectorstore()

    # Step 5: Check whether this PDF already exists
    collection = vectorstore._collection

    existing_documents = collection.get(
        where={
            "document_id": document_id
        }
    )

    if existing_documents["ids"]:
     return {
        "file": file_path,
        "number_of_chunks": len(existing_documents["ids"]),
        "message": "This PDF has already been processed.",
        "already_exists": True,
      }
    # Step 6: Create metadata for each chunk
    metadatas = [
        {
            "document_id": document_id,
            "source": pdf_path.name,
        }
        for _ in chunks
    ]

    # Step 7: Create unique IDs for each chunk
    chunk_ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    # Step 8: Store chunks in ChromaDB
    vectorstore.add_texts(
        texts=chunks,
        metadatas=metadatas,
        ids=chunk_ids,
    )

    return {
        "file": file_path,
        "number_of_chunks": len(chunks),
        "message": "PDF processed and stored in ChromaDB successfully.",
        "already_exists": False,
    }