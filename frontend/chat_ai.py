"""
AI Advisor chat page.

Gives the user a conversational interface to ask Gemini questions about
their spending data. Full transaction history is injected as context so
Gemini always has access to real numbers.
"""

import streamlit as st

from backend.ai_engine import answer_finance_question
from backend.supabase_client import fetch_transactions

SUGGESTED_QUESTIONS = [
    "What was my biggest expense last month?",
    "How much did I spend on food this month?",
    "Which category am I overspending in?",
    "Give me three tips to reduce my spending.",
    "What percentage of my income did I save?",
    "Summarise my spending in bullet points.",
]


def _load_transactions() -> list[dict]:
    if "transactions" not in st.session_state:
        result = fetch_transactions(st.session_state.user_id)
        st.session_state.transactions = result["data"] if not result["error"] else []
    return st.session_state.transactions


def _init_chat_history() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


def _render_message_history() -> None:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _send_message(user_input: str, transactions: list[dict]) -> None:
    # Append user message
    st.session_state.chat_messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply = answer_finance_question(
                    question=user_input,
                    transactions=transactions,
                    chat_history=st.session_state.chat_messages[:-1],
                )
            except Exception as exc:
                reply = f"Sorry, I encountered an error: {exc}"

        st.markdown(reply)

    st.session_state.chat_messages.append({"role": "assistant", "content": reply})


def render() -> None:
    st.title("🤖 AI Finance Advisor")

    _init_chat_history()
    transactions = _load_transactions()

    # ── Sidebar-style info strip ──────────────────────────────────────────────
    if transactions:
        st.caption(
            f"Analysing **{len(transactions)}** transactions in your account. "
            "Ask me anything about your spending."
        )
    else:
        st.warning(
            "No transactions found. Upload a bank statement from the Dashboard "
            "to unlock personalised insights."
        )

    # ── Suggested questions ───────────────────────────────────────────────────
    if not st.session_state.chat_messages:
        st.markdown("**Try asking:**")
        cols = st.columns(3)
        for idx, suggestion in enumerate(SUGGESTED_QUESTIONS):
            with cols[idx % 3]:
                if st.button(suggestion, key=f"sug_{idx}", use_container_width=True):
                    _send_message(suggestion, transactions)
                    st.rerun()

    # ── Message history ───────────────────────────────────────────────────────
    _render_message_history()

    # ── Input box ─────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask about your spending…")
    if user_input:
        _send_message(user_input, transactions)

    # ── Clear chat button ─────────────────────────────────────────────────────
    if st.session_state.chat_messages:
        if st.button("🗑️ Clear chat", key="clear_chat"):
            st.session_state.chat_messages = []
            st.rerun()
