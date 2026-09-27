import os

import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)

UPLOAD_URL = f"{API_BASE_URL}/upload"
ANALYZE_URL = f"{API_BASE_URL}/analyze"


st.set_page_config(
    page_title="Financial Loss Analyzer",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

if "document_name" not in st.session_state:
    st.session_state.document_name = None

if "document_chunks" not in st.session_state:
    st.session_state.document_chunks = 0

if "document_processed" not in st.session_state:
    st.session_state.document_processed = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# APPLICATION TITLE
# =========================================================

st.title("📊 Financial Loss Analyzer")

st.write(
    "Upload a financial PDF and chat with the "
    "Financial Analyst and Financial Advisor agents."
)


# =========================================================
# PDF UPLOAD
# =========================================================

st.header("📄 Upload Financial Report")

uploaded_file = st.file_uploader(
    "Choose a financial PDF",
    type=["pdf"],
)


if uploaded_file is not None:

    if st.button(
        "📥 Upload & Process PDF",
        type="primary"
    ):

        with st.spinner(
            "Uploading and processing PDF..."
        ):

            try:

                response = requests.post(
                    UPLOAD_URL,
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    },
                    timeout=120,
                )

                response.raise_for_status()

                result = response.json()

                st.session_state.document_name = (
                    result["filename"]
                )

                st.session_state.document_chunks = (
                    result["number_of_chunks"]
                )

                st.session_state.document_processed = True

                st.success(
                    result["message"]
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI backend. "
                    "Please make sure FastAPI is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The PDF processing request took too long."
                )

            except requests.exceptions.RequestException as error:

                st.error(
                    f"PDF upload failed: {error}"
                )


# =========================================================
# DOCUMENT STATUS
# =========================================================

if st.session_state.document_processed:

    st.subheader("📄 Current Financial Report")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Document",
            st.session_state.document_name
        )

    with col2:

        st.metric(
            "Status",
            "Processed"
        )

    with col3:

        st.metric(
            "Chunks",
            st.session_state.document_chunks
        )


# =========================================================
# CHAT SECTION
# =========================================================

st.header("💬 Financial AI Chat")


# =========================================================
# CLEAR CHAT
# =========================================================

if st.button("🗑️ Clear Chat"):

    st.session_state.messages = []

    st.rerun()


# =========================================================
# DISPLAY PREVIOUS CHAT MESSAGES
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        # ---------------------------------------------
        # USER MESSAGE
        # ---------------------------------------------

        if message["role"] == "user":

            st.markdown(
                message["content"]
            )

        # ---------------------------------------------
        # ASSISTANT MESSAGE
        # ---------------------------------------------

        elif message["role"] == "assistant":

            financial_analysis = message.get(
                "financial_analysis",
                ""
            )

            recommendations = message.get(
                "recommendations",
                ""
            )

            # Show Financial Analysis only if available
            if financial_analysis.strip():

                st.markdown(
                    "### 📈 Financial Analysis"
                )

                st.markdown(
                    financial_analysis
                )

            # Show Recommendations only if available
            if recommendations.strip():

                st.markdown(
                    "### 💡 Recommendations"
                )

                st.markdown(
                    recommendations
                )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask a question about the financial report..."
)


if question:

    # -----------------------------------------------------
    # Check whether PDF was processed
    # -----------------------------------------------------

    if not st.session_state.document_processed:

        st.warning(
            "Please upload and process a financial PDF first."
        )

    else:

        # -------------------------------------------------
        # BUILD API-SAFE CONVERSATION HISTORY
        # -------------------------------------------------
        #
        # IMPORTANT:
        #
        # Streamlit stores assistant messages as:
        #
        # {
        #     role,
        #     financial_analysis,
        #     recommendations
        # }
        #
        # FastAPI expects:
        #
        # {
        #     role,
        #     content
        # }
        #
        # Therefore we convert the messages here.
        # -------------------------------------------------

        conversation_history = []

        for message in (
            st.session_state.messages[-6:]
        ):

            # ---------------------------------------------
            # Previous user message
            # ---------------------------------------------

            if message["role"] == "user":

                conversation_history.append(
                    {
                        "role": "user",
                        "content": message["content"],
                    }
                )

            # ---------------------------------------------
            # Previous assistant message
            # ---------------------------------------------

            elif message["role"] == "assistant":

                financial_analysis = message.get(
                    "financial_analysis",
                    ""
                )

                recommendations = message.get(
                    "recommendations",
                    ""
                )

                assistant_content = (
                    financial_analysis
                )

                if recommendations.strip():

                    if assistant_content.strip():

                        assistant_content += (
                            "\n\n"
                        )

                    assistant_content += (
                        recommendations
                    )

                conversation_history.append(
                    {
                        "role": "assistant",
                        "content": assistant_content,
                    }
                )

        # -------------------------------------------------
        # DISPLAY CURRENT USER QUESTION
        # -------------------------------------------------

        with st.chat_message("user"):

            st.markdown(
                question
            )

        # -------------------------------------------------
        # SAVE CURRENT USER QUESTION
        # -------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # -------------------------------------------------
        # CALL FASTAPI
        # -------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing financial information..."
            ):

                try:

                    response = requests.post(
                        ANALYZE_URL,
                        json={
                            "question": question,
                            "conversation_history": (
                                conversation_history
                            ),
                        },
                        timeout=120,
                    )

                    response.raise_for_status()

                    result = response.json()

                    # -------------------------------------
                    # Get Financial Analyst response
                    # -------------------------------------

                    financial_analysis = result.get(
                        "financial_analysis",
                        ""
                    )

                    # -------------------------------------
                    # Get Financial Advisor response
                    # -------------------------------------

                    recommendations = result.get(
                        "recommendations",
                        ""
                    )

                    # -------------------------------------
                    # DISPLAY FINANCIAL ANALYSIS
                    # -------------------------------------

                    if financial_analysis.strip():

                        st.markdown(
                            "### 📈 Financial Analysis"
                        )

                        st.markdown(
                            financial_analysis
                        )

                    # -------------------------------------
                    # DISPLAY RECOMMENDATIONS
                    # -------------------------------------

                    if recommendations.strip():

                        st.markdown(
                            "### 💡 Recommendations"
                        )

                        st.markdown(
                            recommendations
                        )

                    # -------------------------------------
                    # SAVE ASSISTANT RESPONSE
                    # -------------------------------------

                    st.session_state.messages.append(
                        {
                            "role": "assistant",

                            "financial_analysis":
                                financial_analysis,

                            "recommendations":
                                recommendations,
                        }
                    )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to the FastAPI backend."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "The analysis request took too long."
                    )

                except requests.exceptions.RequestException as error:

                    st.error(
                        f"API request failed: {error}"
                    )