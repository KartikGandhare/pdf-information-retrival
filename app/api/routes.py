from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

import shutil
from pathlib import Path

from app.graph.workflow import financial_workflow
from app.ingestion.ingest import ingest_pdf


router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class FinancialQuestion(BaseModel):
    question: str

    conversation_history: list[ChatMessage] = Field(
        default_factory=list
    )


@router.get("/health")
def health_check():

    return {
        "status": "ok"
    }


@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    upload_directory = Path("data")

    upload_directory.mkdir(
        exist_ok=True
    )

    safe_filename = Path(
        file.filename
    ).name

    file_path = (
        upload_directory
        / safe_filename
    )

    with file_path.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = ingest_pdf(
        str(file_path)
    )

    return {
        "filename": safe_filename,
        "number_of_chunks": (
            result["number_of_chunks"]
        ),
        "message": result["message"],
        "already_exists": (
            result["already_exists"]
        ),
    }


@router.post("/analyze")
def analyze_financial_question(
    request: FinancialQuestion
):

    result = financial_workflow.invoke(
        {
            "question": request.question,

            "conversation_history": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message
                in request.conversation_history
            ],
        }
    )

    return {
        "question": request.question,

        "financial_analysis": (
            result["financial_analysis"]
        ),

        "recommendations": (
            result.get(
                "recommendations",
                ""
            )
        ),
    }