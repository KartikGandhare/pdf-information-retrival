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


def financial_advisor(
    financial_analysis: str,
    question: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict:

    conversation_history = conversation_history or []

    history = format_conversation_history(
        conversation_history
    )

    prompt = f"""
You are a Financial Advisor Agent.

Your job is to answer the CURRENT user question
using the Financial Analyst's analysis.

CONVERSATION HISTORY:
{history}

FINANCIAL ANALYST REPORT:
{financial_analysis}

CURRENT USER QUESTION:
{question}


IMPORTANT INSTRUCTIONS:

1. First understand exactly what the user is asking.

2. Answer ONLY the current question.

3. Use conversation history to understand
   references such as:
   - it
   - that
   - this
   - the loss
   - the loan
   - the company
   - those numbers

4. Do NOT automatically provide a complete
   list of recommendations for every question.

5. If the user asks for a financial fact,
   answer the fact directly.

6. If the user asks why something happened,
   explain the relevant causes from the
   Financial Analyst's report.

7. If the user asks for recommendations,
   provide practical actions based only on
   the Financial Analyst's findings.

8. Do not invent financial figures.

9. Do not invent facts that are not present
   in the analyst report.

10. Do not claim that any recommendation will
    definitely solve the company's financial loss.

11. Do not repeat unrelated information.

12. Clearly distinguish facts from recommendations.

13. Keep the response concise and focused.


ANSWER STYLE:

Use this structure when appropriate:

Direct Answer:
- Answer the current question.

Recommendations:
- Include recommendations ONLY when the user
  is asking what should be done.

Relevant KPIs:
- Include only KPIs relevant to the current
  question.

Expected Business Impact:
- Include this only when recommendations are
  provided.

Do not include empty sections.
Do not repeat the same information in multiple
sections.
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    recommendations = response_to_text(response)

    return {
        "question": question,
        "recommendations": recommendations,
    }