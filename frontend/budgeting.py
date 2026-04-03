"""
Budgeting page — set monthly limits and track actual vs budget.
AI can suggest limits based on spending history.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.ai_engine import suggest_budgets
from backend.supabase_client import fetch_budgets, fetch_transactions, upsert_budget

CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Entertainment",
    "Utilities", "Rent & Housing", "Healthcare", "Subscriptions", "Other",
]

CATEGORY_COLORS = {
    "Food & Dining":  "#6366f1",
    "Transport":      "#22d3ee",
    "Shopping":       "#f59e0b",
    "Entertainment":  "#ec4899",
    "Utilities":      "#10b981",
    "Rent & Housing": "#f97316",
    "Healthcare":     "#ef4444",
    "Subscriptions":  "#06b6d4",
    "Other":          "#64748b",
}


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    with st.spinner("Loading budget data…"):
        t = fetch_transactions(st.session_state.user_id)
        b = fetch_budgets(st.session_state.user_id)

    txn_df = pd.DataFrame(t["data"] or [])
    bud_df = pd.DataFrame(b["data"] or [])

    if not txn_df.empty:
        txn_df["amount"] = pd.to_numeric(txn_df["amount"], errors="coerce").fillna(0)

    return txn_df, bud_df


def render() -> None:
    st.title("💰 Budgeting")

    txn_df, bud_df = _load_data()
    existing_limits: dict[str, float] = (
        dict(zip(bud_df["category"], bud_df["monthly_limit"]))
        if not bud_df.empty else {}
    )

    # ── AI Budget Suggestions ──────────────────────────────────────────────────
    if not txn_df.empty:
        col_btn, col_note = st.columns([1, 3])
        with col_btn:
            run_ai = st.button("✨ Get AI Budget Suggestions", use_container_width=True)
        with col_note:
            st.caption("Gemini will analyse your spending history and suggest realistic monthly limits.")

        if run_ai:
            with st.spinner("🤖 Analysing your spending history…"):
                suggestions = suggest_budgets(txn_df.to_dict("records"))

            if suggestions:
                st.success("AI suggestions ready — review and apply below.")
                # Store in session state so the form can pick them up
                st.session_state["ai_budget_suggestions"] = {
                    s["category"]: float(s["suggested_limit"]) for s in suggestions
                }
                # Show reasoning
                with st.expander("View AI reasoning", expanded=False):
                    for s in suggestions:
                        st.markdown(
                            f"**{s['category']}** → ${s['suggested_limit']:,.2f}/mo  \n"
                            f"<span style='color:#94a3b8;font-size:0.85rem'>{s.get('reasoning','')}</span>",
                            unsafe_allow_html=True,
                        )
            else:
                st.warning("Couldn't generate suggestions — try uploading more transaction data.")

    st.divider()

    # ── Set Budgets form ──────────────────────────────────────────────────────
    with st.expander("⚙️ Set Monthly Budget Limits", expanded=bud_df.empty):
        ai_suggestions = st.session_state.get("ai_budget_suggestions", {})

        with st.form("budget_form"):
            st.markdown("Set a **monthly limit** per category. AI suggestions are pre-filled if available.")
            cols = st.columns(3)
            inputs: dict[str, float] = {}

            for idx, cat in enumerate(CATEGORIES):
                # Priority: existing saved → AI suggestion → 0
                default = existing_limits.get(cat) or ai_suggestions.get(cat) or 0.0
                with cols[idx % 3]:
                    inputs[cat] = st.number_input(
                        cat, min_value=0.0, value=float(default),
                        step=50.0, format="%.2f",
                    )

            submitted = st.form_submit_button("Save Budgets", use_container_width=True)

        if submitted:
            errors = []
            with st.spinner("Saving budgets…"):
                for cat, limit in inputs.items():
                    if limit > 0:
                        res = upsert_budget(st.session_state.user_id, cat, limit)
                        if res["error"]:
                            errors.append(f"{cat}: {res['error']}")
            if errors:
                st.error("Some budgets failed:\n" + "\n".join(errors))
            else:
                st.success("Budgets saved!")
                if "ai_budget_suggestions" in st.session_state:
                    del st.session_state["ai_budget_suggestions"]
                st.rerun()

    st.divider()

    # ── Budget vs Actual ──────────────────────────────────────────────────────
    st.subheader("Budget vs Actual Spending")

    if bud_df.empty:
        st.info("No budgets set yet. Use the form above or click **Get AI Budget Suggestions**.")
        return

    limits_map = dict(zip(bud_df["category"], bud_df["monthly_limit"]))

    # Actuals — current month if possible
    actuals_map: dict[str, float] = {}
    if not txn_df.empty:
        expenses = txn_df[txn_df["amount"] < 0].copy()
        expenses["amount_abs"] = expenses["amount"].abs()
        if "date" in expenses.columns:
            try:
                expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
                today = pd.Timestamp.now()
                this_month = expenses[
                    (expenses["date"].dt.month == today.month) &
                    (expenses["date"].dt.year  == today.year)
                ]
                if not this_month.empty:
                    expenses = this_month
            except Exception:
                pass
        actuals_map = expenses.groupby("category")["amount_abs"].sum().to_dict()

    budgeted_cats = list(limits_map.keys())

    # ── Grouped bar chart ──────────────────────────────────────────────────────
    budgets_vals = [limits_map[c] for c in budgeted_cats]
    actual_vals  = [actuals_map.get(c, 0) for c in budgeted_cats]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Budget", x=budgeted_cats, y=budgets_vals,
        marker_color="rgba(99,102,241,0.35)",
        marker_line=dict(color="#6366f1", width=1.5),
        text=[f"${v:,.0f}" for v in budgets_vals],
        textposition="outside", textfont=dict(color="#6366f1", size=10),
    ))
    fig.add_trace(go.Bar(
        name="Actual",
        x=budgeted_cats,
        y=actual_vals,
        marker_color=[
            "#ef4444" if actual_vals[i] > budgets_vals[i] else CATEGORY_COLORS.get(c, "#6366f1")
            for i, c in enumerate(budgeted_cats)
        ],
        marker_line_width=0,
        text=[f"${v:,.0f}" for v in actual_vals],
        textposition="outside", textfont=dict(color="#f1f5f9", size=10),
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        xaxis=dict(tickangle=-25, gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$"),
        legend=dict(
            bgcolor="rgba(30,41,59,0.8)", bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1, font=dict(color="#94a3b8"),
        ),
        margin=dict(t=20, b=60),
        bargap=0.25, bargroupgap=0.05,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Status table ──────────────────────────────────────────────────────────
    st.subheader("Category Status")
    rows = []
    for cat in budgeted_cats:
        limit   = limits_map[cat]
        actual  = actuals_map.get(cat, 0.0)
        pct     = (actual / limit * 100) if limit > 0 else 0.0
        remaining = limit - actual
        status  = (
            "🔴 Over budget"    if actual > limit
            else "🟡 Near limit" if pct >= 80
            else "🟢 On track"
        )
        rows.append({
            "Category":       cat,
            "Budget ($)":     round(limit, 2),
            "Spent ($)":      round(actual, 2),
            "Remaining ($)":  round(remaining, 2),
            "Used (%)":       round(pct, 1),
            "Status":         status,
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
