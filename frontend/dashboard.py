"""
Dashboard page — PDF upload, transaction processing, and spending charts.
"""

import os
import tempfile

import pandas as pd
import plotly.express as px
import streamlit as st

from backend.ai_engine import extract_transactions_from_markdown
from backend.document_parser import parse_pdf_to_markdown
from backend.supabase_client import fetch_transactions, insert_transactions


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _load_transactions() -> list[dict]:
    """Fetch transactions from Supabase and cache in session state."""
    result = fetch_transactions(st.session_state.user_id)
    if result["error"]:
        st.error(f"Could not load transactions: {result['error']}")
        return []
    st.session_state.transactions = result["data"]
    return result["data"]


def _process_uploaded_pdf(uploaded_file) -> None:
    """Full pipeline: PDF → Reducto → Gemini → Supabase."""

    # ── 1. Save to a temp file ────────────────────────────────────────────────
    suffix = os.path.splitext(uploaded_file.name)[-1] or ".pdf"
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        # ── 2. Reducto — extract Markdown ─────────────────────────────────────
        with st.spinner("📄 Extracting text from PDF (Reducto)…"):
            markdown_text = parse_pdf_to_markdown(tmp_path)

        st.success(f"PDF parsed — {len(markdown_text):,} characters extracted.")

        # ── 3. Gemini — extract transactions ──────────────────────────────────
        with st.spinner("🤖 Identifying transactions (Gemini)…"):
            transactions = extract_transactions_from_markdown(markdown_text)

        if not transactions:
            st.warning("No transactions were found in this document.")
            return

        st.success(f"Found **{len(transactions)}** transactions.")

        # Preview before saving
        with st.expander("Preview extracted transactions", expanded=True):
            st.dataframe(
                pd.DataFrame(transactions),
                use_container_width=True,
                hide_index=True,
            )

        # ── 4. Save to Supabase ───────────────────────────────────────────────
        with st.spinner("💾 Saving to database…"):
            result = insert_transactions(
                user_id=st.session_state.user_id,
                transactions=transactions,
                source_file=uploaded_file.name,
            )

        if result["error"]:
            st.error(f"Database error: {result['error']}")
            return

        st.success("Transactions saved successfully!")
        # Refresh cached transactions
        _load_transactions()
        st.rerun()

    except Exception as exc:
        st.error(f"Processing failed: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ─── Charts ───────────────────────────────────────────────────────────────────

def _render_charts(df: pd.DataFrame) -> None:
    expenses = df[df["amount"] < 0].copy()
    expenses["amount_abs"] = expenses["amount"].abs()

    if expenses.empty:
        st.info("No expense transactions to chart yet.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Spending by Category")
        cat_totals = (
            expenses.groupby("category")["amount_abs"]
            .sum()
            .reset_index()
            .rename(columns={"amount_abs": "Total Spent"})
            .sort_values("Total Spent", ascending=False)
        )
        fig_pie = px.pie(
            cat_totals,
            names="category",
            values="Total Spent",
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Category Breakdown")
        fig_bar = px.bar(
            cat_totals,
            x="Total Spent",
            y="category",
            orientation="h",
            text_auto=".2s",
            color="Total Spent",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Monthly trend (if date data is available)
    if "date" in df.columns and df["date"].notna().any():
        st.subheader("Monthly Spending Trend")
        trend = expenses.copy()
        trend["date"] = pd.to_datetime(trend["date"], errors="coerce")
        trend = trend.dropna(subset=["date"])
        trend["month"] = trend["date"].dt.to_period("M").astype(str)
        monthly = (
            trend.groupby(["month", "category"])["amount_abs"]
            .sum()
            .reset_index()
        )
        if not monthly.empty:
            fig_line = px.bar(
                monthly,
                x="month",
                y="amount_abs",
                color="category",
                labels={"amount_abs": "Amount ($)", "month": "Month"},
            )
            fig_line.update_layout(margin=dict(t=10, b=10))
            st.plotly_chart(fig_line, use_container_width=True)


# ─── Main render function ─────────────────────────────────────────────────────

def render() -> None:
    st.title("📊 Dashboard")

    # ── Upload section ────────────────────────────────────────────────────────
    st.subheader("Upload Bank Statement")
    uploaded_file = st.file_uploader(
        "Drop a PDF bank statement here",
        type=["pdf"],
        help="Supported: most bank-exported PDF statements",
    )

    if uploaded_file is not None:
        # Guard against reprocessing after a rerun
        last_key = "last_uploaded_file"
        if st.session_state.get(last_key) != uploaded_file.name + str(uploaded_file.size):
            st.session_state[last_key] = uploaded_file.name + str(uploaded_file.size)
            _process_uploaded_pdf(uploaded_file)

    st.divider()

    # ── Transaction data ──────────────────────────────────────────────────────
    st.subheader("Your Transactions")

    if "transactions" not in st.session_state or st.button("🔄 Refresh"):
        transactions = _load_transactions()
    else:
        transactions = st.session_state.transactions

    if not transactions:
        st.info("No transactions yet. Upload a PDF statement above to get started.")
        return

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    total_income   = df[df["amount"] > 0]["amount"].sum()
    total_expenses = df[df["amount"] < 0]["amount"].abs().sum()
    net            = total_income - total_expenses

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Transactions", len(df))
    k2.metric("Total Income",    f"${total_income:,.2f}")
    k3.metric("Total Expenses",  f"${total_expenses:,.2f}")
    k4.metric("Net",             f"${net:,.2f}", delta=f"${net:,.2f}")

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    _render_charts(df)

    # ── Raw table ─────────────────────────────────────────────────────────────
    st.subheader("All Transactions")
    display_cols = [c for c in ["date", "description", "amount", "category", "source_file"] if c in df.columns]
    st.dataframe(
        df[display_cols].sort_values("date", ascending=False, na_position="last"),
        use_container_width=True,
        hide_index=True,
    )
