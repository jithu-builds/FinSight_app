"""
Budgeting page — set monthly category budgets and track actual vs target.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.supabase_client import (
    fetch_budgets,
    fetch_transactions,
    upsert_budget,
)

CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Rent & Housing",
    "Healthcare",
    "Subscriptions",
    "Other",
]


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (transactions_df, budgets_df)."""
    t_result = fetch_transactions(st.session_state.user_id)
    b_result = fetch_budgets(st.session_state.user_id)

    txn_df = pd.DataFrame(t_result["data"] or [])
    bud_df = pd.DataFrame(b_result["data"] or [])

    if not txn_df.empty:
        txn_df["amount"] = pd.to_numeric(txn_df["amount"], errors="coerce").fillna(0)

    return txn_df, bud_df


def _budget_vs_actual_chart(
    categories: list[str],
    actuals: dict[str, float],
    limits: dict[str, float],
) -> None:
    budgeted = [limits.get(c, 0) for c in categories]
    spent    = [actuals.get(c, 0) for c in categories]

    bar_colors = [
        "#e74c3c" if spent[i] > budgeted[i] and budgeted[i] > 0 else "#2ecc71"
        for i in range(len(categories))
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(name="Budget", x=categories, y=budgeted, marker_color="#3498db", opacity=0.6)
    )
    fig.add_trace(
        go.Bar(name="Actual", x=categories, y=spent, marker_color=bar_colors)
    )
    fig.update_layout(
        barmode="group",
        xaxis_tickangle=-30,
        yaxis_title="Amount ($)",
        margin=dict(t=20, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def render() -> None:
    st.title("💰 Budget Tracker")

    txn_df, bud_df = _load_data()

    if txn_df.empty:
        st.info("No transaction data found. Upload a bank statement from the Dashboard first.")

    # ── Set Budgets form ──────────────────────────────────────────────────────
    with st.expander("⚙️ Set Monthly Budget Limits", expanded=bud_df.empty):
        existing_limits: dict[str, float] = {}
        if not bud_df.empty:
            existing_limits = dict(zip(bud_df["category"], bud_df["monthly_limit"]))

        with st.form("budget_form"):
            st.markdown("Enter a **monthly limit** for each category (leave 0 to skip).")
            cols = st.columns(3)
            inputs: dict[str, float] = {}
            for idx, cat in enumerate(CATEGORIES):
                with cols[idx % 3]:
                    inputs[cat] = st.number_input(
                        cat,
                        min_value=0.0,
                        value=float(existing_limits.get(cat, 0.0)),
                        step=50.0,
                        format="%.2f",
                    )
            submitted = st.form_submit_button("Save Budgets", use_container_width=True)

        if submitted:
            errors = []
            for cat, limit in inputs.items():
                if limit > 0:
                    res = upsert_budget(st.session_state.user_id, cat, limit)
                    if res["error"]:
                        errors.append(f"{cat}: {res['error']}")
            if errors:
                st.error("Some budgets failed to save:\n" + "\n".join(errors))
            else:
                st.success("Budgets saved!")
                st.rerun()

    st.divider()

    # ── Budget vs Actual ──────────────────────────────────────────────────────
    st.subheader("Budget vs Actual Spending")

    if bud_df.empty:
        st.info("Set your budget limits above to see the comparison.")
        return

    limits_map = dict(zip(bud_df["category"], bud_df["monthly_limit"]))

    # Calculate actuals (expenses only, current month if dates available)
    actuals_map: dict[str, float] = {}
    if not txn_df.empty:
        expenses = txn_df[txn_df["amount"] < 0].copy()
        expenses["amount_abs"] = expenses["amount"].abs()

        # Filter to current month if date column exists
        if "date" in expenses.columns:
            try:
                expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
                today = pd.Timestamp.now()
                current_month = expenses[
                    (expenses["date"].dt.month == today.month)
                    & (expenses["date"].dt.year  == today.year)
                ]
                if not current_month.empty:
                    expenses = current_month
            except Exception:
                pass

        actuals_map = (
            expenses.groupby("category")["amount_abs"]
            .sum()
            .to_dict()
        )

    budgeted_categories = list(limits_map.keys())
    _budget_vs_actual_chart(budgeted_categories, actuals_map, limits_map)

    # ── Status table ──────────────────────────────────────────────────────────
    st.subheader("Category Status")
    rows = []
    for cat in budgeted_categories:
        limit  = limits_map[cat]
        actual = actuals_map.get(cat, 0.0)
        pct    = (actual / limit * 100) if limit > 0 else 0.0
        status = (
            "🔴 Over budget"   if actual > limit
            else "🟡 Near limit" if pct >= 80
            else "🟢 On track"
        )
        rows.append(
            {
                "Category":      cat,
                "Budget ($)":    round(limit, 2),
                "Spent ($)":     round(actual, 2),
                "Remaining ($)": round(limit - actual, 2),
                "Used (%)":      round(pct, 1),
                "Status":        status,
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )
