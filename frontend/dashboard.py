"""
Dashboard page — PDF upload, transaction processing, and spending charts.
"""

import os
import tempfile

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.ai_engine import extract_transactions_from_markdown
from backend.document_parser import parse_pdf_to_markdown
from backend.supabase_client import fetch_transactions, file_already_imported, insert_transactions

# Consistent, vibrant colour palette that reads well on dark backgrounds
CATEGORY_COLORS = {
    "Food & Dining":  "#6366f1",
    "Transport":      "#22d3ee",
    "Shopping":       "#f59e0b",
    "Entertainment":  "#ec4899",
    "Utilities":      "#10b981",
    "Rent & Housing": "#f97316",
    "Healthcare":     "#ef4444",
    "Income":         "#84cc16",
    "Transfer":       "#a78bfa",
    "Subscriptions":  "#06b6d4",
    "Other":          "#64748b",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", size=12),
    margin=dict(t=10, b=10, l=10, r=10),
)


def _load_transactions() -> list[dict]:
    with st.spinner("Loading your transactions…"):
        result = fetch_transactions(st.session_state.user_id)
    if result["error"]:
        st.error(f"Could not load transactions: {result['error']}")
        return []
    st.session_state.transactions = result["data"]
    return result["data"]


def _process_uploaded_pdf(uploaded_file) -> None:
    suffix   = os.path.splitext(uploaded_file.name)[-1] or ".pdf"
    tmp_path = ""

    progress_bar = st.progress(0, text="Starting…")
    status_box   = st.empty()

    def update(pct: int, msg: str) -> None:
        progress_bar.progress(pct, text=msg)
        status_box.info(msg)

    try:
        update(5,  "📁 Preparing file…")
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        update(15, "📤 Uploading PDF to Reducto…")
        markdown_text = parse_pdf_to_markdown(tmp_path)
        update(45, f"📄 Text extracted — {len(markdown_text):,} characters.")

        update(55, "🤖 Asking Gemini 2.5 Flash to identify transactions…")
        transactions = extract_transactions_from_markdown(markdown_text)
        update(80, f"✅ Found {len(transactions)} transactions.")

        if not transactions:
            progress_bar.empty(); status_box.empty()
            st.warning("No transactions were found in this document.")
            return

        update(88, "💾 Saving to database…")
        result = insert_transactions(
            user_id=st.session_state.user_id,
            transactions=transactions,
            source_file=uploaded_file.name,
        )

        if result["error"]:
            progress_bar.empty(); status_box.empty()
            st.error(f"Database error: {result['error']}")
            return

        update(100, "🎉 All done!")
        progress_bar.empty(); status_box.empty()

        st.success(f"Imported **{len(transactions)}** transactions from **{uploaded_file.name}**.")
        with st.expander("Preview extracted transactions", expanded=True):
            st.dataframe(pd.DataFrame(transactions), use_container_width=True, hide_index=True)

        _load_transactions()
        st.rerun()

    except Exception as exc:
        progress_bar.empty(); status_box.empty()
        st.error(f"Processing failed: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _get_color_sequence(categories: list[str]) -> list[str]:
    default_colors = list(CATEGORY_COLORS.values())
    return [CATEGORY_COLORS.get(c, default_colors[i % len(default_colors)])
            for i, c in enumerate(categories)]


def _render_charts(df: pd.DataFrame) -> None:
    expenses = df[df["amount"] < 0].copy()
    expenses["amount_abs"] = expenses["amount"].abs()

    if expenses.empty:
        st.info("No expense transactions to chart yet.")
        return

    cat_totals = (
        expenses.groupby("category")["amount_abs"]
        .sum().reset_index()
        .rename(columns={"amount_abs": "Total Spent"})
        .sort_values("Total Spent", ascending=False)
    )
    categories  = cat_totals["category"].tolist()
    color_seq   = _get_color_sequence(categories)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Spending by Category")
        fig = px.pie(
            cat_totals, names="category", values="Total Spent",
            hole=0.45, color="category",
            color_discrete_map=CATEGORY_COLORS,
        )
        fig.update_traces(
            textposition="inside", textinfo="percent+label",
            textfont_size=11,
            marker=dict(line=dict(color="#0f172a", width=2)),
        )
        fig.update_layout(**PLOT_LAYOUT, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Category Breakdown")
        fig = go.Figure(go.Bar(
            x=cat_totals["Total Spent"],
            y=cat_totals["category"],
            orientation="h",
            text=[f"${v:,.0f}" for v in cat_totals["Total Spent"]],
            textposition="outside",
            textfont=dict(color="#f1f5f9", size=11),
            marker_color=color_seq,
            marker_line_width=0,
        ))
        fig.update_layout(
            **PLOT_LAYOUT,
            yaxis=dict(categoryorder="total ascending", tickfont=dict(color="#94a3b8")),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            bargap=0.3,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Monthly trend
    if "date" in df.columns and df["date"].notna().any():
        st.subheader("Monthly Spending Trend")
        trend = expenses.copy()
        trend["date"] = pd.to_datetime(trend["date"], errors="coerce")
        trend = trend.dropna(subset=["date"])
        trend["month"] = trend["date"].dt.to_period("M").astype(str)
        monthly = trend.groupby(["month", "category"])["amount_abs"].sum().reset_index()

        if not monthly.empty:
            fig = px.bar(
                monthly, x="month", y="amount_abs", color="category",
                labels={"amount_abs": "Amount ($)", "month": "Month"},
                color_discrete_map=CATEGORY_COLORS,
            )
            fig.update_layout(
                **PLOT_LAYOUT,
                xaxis=dict(tickfont=dict(color="#94a3b8")),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
                legend=dict(
                    bgcolor="rgba(30,41,59,0.8)", bordercolor="rgba(255,255,255,0.1)",
                    borderwidth=1, font=dict(color="#94a3b8"),
                ),
                bargap=0.2,
            )
            st.plotly_chart(fig, use_container_width=True)


def render() -> None:
    st.title("📊 Dashboard")

    # Upload section
    st.subheader("Upload Bank Statement")

    uploaded_file = st.file_uploader(
        "Select a PDF bank statement", type=["pdf"],
        help="Supported: most bank-exported PDF statements",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        col_btn, col_info, _ = st.columns([1, 3, 2])

        with col_info:
            st.markdown(
                f"<div style='padding:0.55rem 0;color:#94a3b8;font-size:0.875rem'>"
                f"📄 <b style='color:#f1f5f9'>{uploaded_file.name}</b> "
                f"({uploaded_file.size / 1024:.1f} KB) ready to upload</div>",
                unsafe_allow_html=True,
            )

        with col_btn:
            upload_clicked = st.button(
                "⬆️ Upload & Process", type="primary", use_container_width=True
            )

        if upload_clicked:
            # Clear any previous error state so the same file can be retried
            st.session_state.pop("last_uploaded_file", None)

            already_imported = file_already_imported(
                st.session_state.user_id, uploaded_file.name
            )
            if already_imported:
                st.warning(
                    f"**{uploaded_file.name}** was already imported. "
                    "Duplicate rows will be skipped automatically by the database."
                )
                col_yes, col_no, _ = st.columns([1, 1, 4])
                with col_yes:
                    if st.button("Import anyway", key="confirm_reimport"):
                        _process_uploaded_pdf(uploaded_file)
                with col_no:
                    if st.button("Cancel", key="cancel_reimport"):
                        st.rerun()
            else:
                _process_uploaded_pdf(uploaded_file)

    st.divider()

    # Transactions section
    st.subheader("Your Transactions")
    if "transactions" not in st.session_state:
        transactions = _load_transactions()
    else:
        transactions = st.session_state.transactions

    if not transactions:
        st.info("No transactions yet. Upload a PDF statement above to get started.")
        return

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    total_income   = df[df["amount"] > 0]["amount"].sum()
    total_expenses = df[df["amount"] < 0]["amount"].abs().sum()
    net            = total_income - total_expenses

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Transactions",   len(df))
    k2.metric("Total Income",   f"${total_income:,.2f}")
    k3.metric("Total Expenses", f"${total_expenses:,.2f}")
    k4.metric("Net",            f"${net:,.2f}")

    st.divider()
    _render_charts(df)

    st.subheader("All Transactions")
    display_cols = [c for c in ["date", "description", "amount", "category", "source_file"] if c in df.columns]
    st.dataframe(
        df[display_cols].sort_values("date", ascending=False, na_position="last"),
        use_container_width=True, hide_index=True,
    )
