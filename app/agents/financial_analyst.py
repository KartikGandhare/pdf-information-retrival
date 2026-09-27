from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import GEMINI_API_KEY, LLM_MODEL


def get_llm():
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0,
    )


def response_to_text(response):
    if isinstance(response.content, str):
        return response.content

    if isinstance(response.content, list):
        return "\n".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    return str(response.content)


def format_conversation_history(
    conversation_history: list[dict[str, str]]
) -> str:

    if not conversation_history:
        return "No previous conversation."

    return "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in conversation_history[-6:]
    )


def financial_analyst(
    question: str,
    retrieved_documents: list[str],
    conversation_history: list[dict[str, str]] | None = None,
) -> dict:

    conversation_history = conversation_history or []

    if not retrieved_documents:
        return {
            "question": question,
            "retrieved_context": "",
            "analysis": (
                "No relevant financial information "
                "was found."
            )
        }

    context = "\n\n".join(retrieved_documents)

    history = format_conversation_history(
        conversation_history
    )

    prompt = f"""
You are a Financial Analyst Agent.

Your job is to answer the CURRENT user question
using the financial document as the source of truth.

CONVERSATION HISTORY:
{history}

FINANCIAL DOCUMENT:
{context}

CURRENT USER QUESTION:
{question}


IMPORTANT INSTRUCTIONS:

1. First understand exactly what the user is asking.

2. Answer ONLY the current question.

3. Use the conversation history to understand
   references such as:
   - it
   - that
   - this
   - the loss
   - the loan
   - the company
   - those numbers

4. Do NOT automatically provide the entire
   financial report.

5. If the user asks for a specific fact,
   provide that fact directly.

6. If the user asks "why", explain the relevant
   causes from the financial document.

7. If the user asks "how much", provide the
   relevant financial amount.

8. If the user asks about sales, discuss sales.

9. If the user asks about costs, discuss costs.

10. If the user asks about the loan, discuss
    the loan and related interest.

11. If the user asks for recommendations,
    provide the financial facts needed to
    understand the problem, but do not create
    recommendations that are not supported
    by the document.

12. Do not repeat unrelated financial figures.

13. Do not invent financial information.

14. Clearly distinguish reported facts from
    your analysis.

15. Perform simple calculations only when the
    required numbers are available.

16. If the financial document contains numbers
    that do not mathematically reconcile, do not
    invent a missing number. State the documented
    figure and mention the inconsistency when
    relevant to the question.


ANSWER STYLE:

Keep the answer concise and focused.

Use this structure:

Direct Answer:
- Answer the user's current question.

Supporting Facts:
- Include only facts relevant to the question.

Analysis:
- Include this section only when analysis is
  actually useful for answering the question.

Do not include empty sections.
Do not repeat the same information in multiple
sections.
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    analysis = response_to_text(response)

    return {
        "question": question,
        "retrieved_context": context,
        "analysis": analysis,
    }