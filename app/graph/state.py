from typing import TypedDict


class FinancialState(TypedDict, total=False):
    question: str
    conversation_history: list[dict[str, str]]
    retrieved_documents: list[str]
    financial_analysis: str
    recommendations: str