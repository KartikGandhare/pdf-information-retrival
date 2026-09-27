from langgraph.graph import StateGraph, START, END

from app.graph.state import FinancialState

from app.rag.retriever import get_retriever

from app.agents.financial_analyst import financial_analyst
from app.agents.financial_advisor import financial_advisor


def retrieve_documents(state: FinancialState):

    retriever = get_retriever()

    history = state.get(
        "conversation_history",
        []
    )

    previous_questions = [
        message["content"]
        for message in history[-6:]
        if message.get("role") == "user"
    ]

    retrieval_query_parts = (
        previous_questions[-2:]
        + [state["question"]]
    )

    retrieval_query = "\n".join(
        retrieval_query_parts
    )

    documents = retriever.invoke(
        retrieval_query
    )

    retrieved_documents = [
        document.page_content
        for document in documents
    ]

    return {
        "retrieved_documents": retrieved_documents
    }


def run_financial_analyst(
    state: FinancialState
):

    result = financial_analyst(
        question=state["question"],
        retrieved_documents=state[
            "retrieved_documents"
        ],
        conversation_history=state.get(
            "conversation_history",
            []
        ),
    )

    return {
        "financial_analysis": result["analysis"]
    }


def should_use_financial_advisor(
    state: FinancialState
):
    """
    Decide whether the user's current question
    requires financial recommendations.
    """

    question = state["question"].lower()

    advice_keywords = [
        "what should",
        "what can",
        "how should",
        "how can",
        "recommend",
        "recommendation",
        "advice",
        "suggest",
        "suggestion",
        "action",
        "actions",
        "improve",
        "reduce the loss",
        "overcome the loss",
        "solve the problem",
        "what do we do",
        "what can management do",
        "what should management do",
    ]

    for keyword in advice_keywords:

        if keyword in question:
            return "financial_advisor"

    return END


def run_financial_advisor(
    state: FinancialState
):

    result = financial_advisor(
        financial_analysis=state[
            "financial_analysis"
        ],
        question=state["question"],
        conversation_history=state.get(
            "conversation_history",
            []
        ),
    )

    return {
        "recommendations": result[
            "recommendations"
        ]
    }


def build_workflow():

    workflow = StateGraph(
        FinancialState
    )

    workflow.add_node(
        "retrieve_documents",
        retrieve_documents
    )

    workflow.add_node(
        "financial_analyst",
        run_financial_analyst
    )

    workflow.add_node(
        "financial_advisor",
        run_financial_advisor
    )

    workflow.add_edge(
        START,
        "retrieve_documents"
    )

    workflow.add_edge(
        "retrieve_documents",
        "financial_analyst"
    )

    workflow.add_conditional_edges(
        "financial_analyst",
        should_use_financial_advisor,
        {
            "financial_advisor":
                "financial_advisor",

            END:
                END,
        }
    )

    workflow.add_edge(
        "financial_advisor",
        END
    )

    return workflow.compile()


financial_workflow = build_workflow()