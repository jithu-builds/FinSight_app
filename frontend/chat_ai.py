"""
AI Insights page.

Auto-analyses the user's transaction history against their budgets and surfaces:
  • A spending health score
  • Budget alerts (categories close to or over the limit)
  • Predicted end-of-month spend per category
  • Specific, actionable recommendations (e.g. "Skip the cinema this weekend")
  • A follow-up chat for custom questions
"""

import plotly.graph_objects as go
import streamlit as st

from backend.ai_engine import answer_finance_question, generate_spending_insights
from backend.supabase_client import fetch_budgets, fetch_transactions

# ── Colour helpers ────────────────────────────────────────────────────────────

SEVERITY_STYLE = {
    "high":   ("🔴", "#ef4444", "rgba(239,68,68,0.1)"),
    "medium": ("🟡", "#f59e0b", "rgba(245,158,11,0.1)"),
    "low":    ("🟢", "#22c55e", "rgba(34,197,94,0.1)"),
}


def _score_color(score: int) -> str:
    if score >= 75: return "#22c55e"
    if score >= 50: return "#f59e0b"
    return "#ef4444"


def _score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 65: return "Good"
    if score >= 50: return "Fair"
    if score >= 30: return "Needs attention"
    return "Over budget"


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_data() -> tuple[list[dict], list[dict]]:
    with st.spinner("Loading your financial data…"):
        t = fetch_transactions(st.session_state.user_id)
        b = fetch_budgets(st.session_state.user_id)
    transactions = t["data"] if not t["error"] else []
    budgets      = b["data"] if not b["error"] else []
    st.session_state.transactions = transactions
    return transactions, budgets


# ── Section renderers ─────────────────────────────────────────────────────────

def _render_health_score(score: int, summary: str) -> None:
    color = _score_color(score)
    label = _score_label(score)

    col_score, col_summary = st.columns([1, 3])

    with col_score:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "", "font": {"size": 36, "color": color}},
            gauge={
                "axis":      {"range": [0, 100], "tickcolor": "#475569", "tickwidth": 1},
                "bar":       {"color": color, "thickness": 0.25},
                "bgcolor":   "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  30], "color": "rgba(239,68,68,0.15)"},
                    {"range": [30, 65], "color": "rgba(245,158,11,0.12)"},
                    {"range": [65,100], "color": "rgba(34,197,94,0.12)"},
                ],
            },
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            height=200,
            margin=dict(t=20, b=0, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            f"<p style='text-align:center;font-size:1rem;font-weight:700;color:{color};margin-top:-12px'>"
            f"{label}</p>",
            unsafe_allow_html=True,
        )

    with col_summary:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.07);
                border-left:3px solid {color};
                border-radius:12px;padding:1.1rem 1.3rem;
            ">
                <p style="color:#e2e8f0;font-size:0.95rem;margin:0;line-height:1.6">{summary}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_alerts(alerts: list[dict]) -> None:
    if not alerts:
        st.success("No budget alerts — you're on track across all categories.")
        return

    cols = st.columns(min(len(alerts), 3))
    for i, alert in enumerate(alerts):
        icon, color, bg = SEVERITY_STYLE.get(alert.get("severity", "low"), SEVERITY_STYLE["low"])
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="
                    background:{bg};border:1px solid {color}33;
                    border-radius:12px;padding:1rem;margin-bottom:0.5rem;
                ">
                    <div style="font-size:0.75rem;font-weight:700;color:{color};
                                text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px">
                        {icon} {alert.get('category','')}
                    </div>
                    <div style="color:#e2e8f0;font-size:0.875rem;line-height:1.5">
                        {alert.get('message','')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_predictions(predictions: list[dict]) -> None:
    if not predictions:
        st.info("Not enough data to generate predictions yet.")
        return

    for pred in predictions:
        cat       = pred.get("category", "")
        spent     = float(pred.get("spent_so_far", 0))
        predicted = float(pred.get("predicted_monthly_total", 0))
        budget    = pred.get("budget")
        exceed    = pred.get("will_exceed", False)
        reason    = pred.get("reason", "")

        budget_val   = float(budget) if budget else None
        pct          = min((predicted / budget_val * 100), 100) if budget_val else None
        bar_color    = "#ef4444" if exceed else "#6366f1"
        status_icon  = "⚠️" if exceed else "✅"

        st.markdown(
            f"""
            <div style="
                background:#1e293b;border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem;
            ">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="font-weight:600;color:#f1f5f9">{status_icon} {cat}</span>
                    <span style="font-size:0.8rem;color:#64748b">{reason}</span>
                </div>
                <div style="display:flex;gap:2rem;margin-bottom:10px">
                    <div>
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Spent so far</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#f1f5f9">${spent:,.2f}</div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Predicted total</div>
                        <div style="font-size:1.1rem;font-weight:700;color:{'#ef4444' if exceed else '#f59e0b'}">${predicted:,.2f}</div>
                    </div>
                    {f'<div><div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Budget</div><div style="font-size:1.1rem;font-weight:700;color:#94a3b8">${budget_val:,.2f}</div></div>' if budget_val else ''}
                </div>
                {f'<div style="background:rgba(255,255,255,0.06);border-radius:99px;height:6px;overflow:hidden"><div style="height:100%;width:{pct:.1f}%;background:{bar_color};border-radius:99px;transition:width 0.3s"></div></div>' if pct is not None else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_recommendations(recommendations: list[dict]) -> None:
    if not recommendations:
        st.info("No specific recommendations right now — keep it up!")
        return

    for rec in recommendations:
        savings = float(rec.get("estimated_savings", 0))
        cat     = rec.get("category", "")
        title   = rec.get("title", "")
        detail  = rec.get("detail", "")

        st.markdown(
            f"""
            <div style="
                background:#1e293b;
                border:1px solid rgba(99,102,241,0.2);
                border-left:3px solid #6366f1;
                border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem;
                display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;
            ">
                <div style="flex:1">
                    <div style="font-weight:600;color:#f1f5f9;margin-bottom:4px">💡 {title}</div>
                    <div style="font-size:0.875rem;color:#94a3b8;line-height:1.5">{detail}</div>
                    <div style="font-size:0.75rem;color:#6366f1;margin-top:6px;font-weight:600">
                        {cat}
                    </div>
                </div>
                {f'<div style="text-align:center;min-width:80px"><div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Save up to</div><div style="font-size:1.2rem;font-weight:700;color:#22c55e">${savings:,.0f}</div></div>' if savings > 0 else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    st.title("🧠 AI Insights")
    st.caption("Real-time analysis of your spending patterns, predictions, and actionable recommendations.")

    transactions, budgets = _load_data()

    if not transactions:
        st.info("No transaction data yet. Upload a bank statement from the Dashboard to unlock AI insights.")
        return

    # Generate / cache insights
    cache_key = f"insights_{st.session_state.user_id}"
    col_refresh, _ = st.columns([1, 5])
    with col_refresh:
        refresh = st.button("🔄 Refresh insights")

    if cache_key not in st.session_state or refresh:
        with st.spinner("🤖 Gemini 2.5 Flash is analysing your spending patterns…"):
            try:
                insights = generate_spending_insights(transactions, budgets)
                st.session_state[cache_key] = insights
            except Exception as exc:
                st.error(f"Could not generate insights: {exc}")
                return
    else:
        insights = st.session_state[cache_key]

    # ── Spending Health Score ─────────────────────────────────────────────────
    st.subheader("Spending Health")
    _render_health_score(
        insights.get("health_score", 50),
        insights.get("summary", ""),
    )

    st.divider()

    # ── Alerts ────────────────────────────────────────────────────────────────
    st.subheader("⚠️ Budget Alerts")
    _render_alerts(insights.get("alerts", []))

    st.divider()

    # ── Predictions ───────────────────────────────────────────────────────────
    st.subheader("📈 End-of-Month Predictions")
    st.caption("Based on your spending pace this month.")
    _render_predictions(insights.get("predictions", []))

    st.divider()

    # ── Recommendations ───────────────────────────────────────────────────────
    st.subheader("💡 Recommendations")
    st.caption("Specific actions based on your actual transaction patterns.")
    _render_recommendations(insights.get("recommendations", []))

    st.divider()

    # ── Follow-up chat ────────────────────────────────────────────────────────
    st.subheader("💬 Ask a Follow-up Question")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything about your spending…"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    reply = answer_finance_question(
                        prompt, transactions,
                        chat_history=st.session_state.chat_messages[:-1],
                    )
                except Exception as exc:
                    reply = f"Error: {exc}"
            st.markdown(reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

    if st.session_state.chat_messages:
        if st.button("🗑️ Clear chat"):
            st.session_state.chat_messages = []
            st.rerun()
