"""
Google Gemini AI engine — gemini-2.5-flash

Three responsibilities:
  1. extract_transactions_from_markdown() — bank statement → JSON transactions
  2. generate_spending_insights()         — spending analysis, predictions, recommendations
  3. answer_finance_question()            — follow-up chat
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime, date

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
_MODEL_NAME = "gemini-2.5-flash"

VALID_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Entertainment",
    "Utilities", "Rent & Housing", "Healthcare", "Income",
    "Transfer", "Subscriptions", "Other",
]


def _get_model():
    import google.generativeai as genai
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is not set in your .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(_MODEL_NAME)


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


# ─── 1. Transaction Extraction ────────────────────────────────────────────────

def extract_transactions_from_markdown(markdown_text: str) -> list[dict]:
    import google.generativeai as genai

    cats = ", ".join(VALID_CATEGORIES)
    prompt = f"""You are a financial data extraction assistant.

Extract EVERY transaction from the bank statement below.

Output fields per transaction:
  - "date"        : YYYY-MM-DD (best guess if partial)
  - "description" : merchant/payee, clean, max 60 chars
  - "amount"      : numeric; NEGATIVE = debit/expense, POSITIVE = credit/income
  - "category"    : one of: {cats}

RULES: Output ONLY a valid JSON array. No markdown, no explanation, no code fences.

Bank statement:
─────────────────
{markdown_text}
─────────────────
JSON array:"""

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1),
        )
        raw = response.text
    except Exception as exc:
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

    cleaned = _strip_fences(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemini returned invalid JSON.\nError: {exc}\nRaw (500 chars): {cleaned[:500]}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}.")

    for t in data:
        try:
            t["amount"] = float(t.get("amount") or 0)
        except (TypeError, ValueError):
            t["amount"] = 0.0

    return data


# ─── 2. Spending Insights ─────────────────────────────────────────────────────

def generate_spending_insights(transactions: list[dict], budgets: list[dict]) -> dict:
    """
    Analyse spending history against budgets and return structured insights.

    Returns a dict with keys:
        summary          str   — 2-3 sentence overview
        health_score     int   — 0-100 budget adherence score
        alerts           list  — categories at risk
        predictions      list  — predicted end-of-month spend per category
        recommendations  list  — specific actionable tips (e.g. skip movies)
    """
    import google.generativeai as genai
    import pandas as pd

    if not transactions:
        return {
            "summary": "No transactions found. Upload a bank statement to get insights.",
            "health_score": 0,
            "alerts": [],
            "predictions": [],
            "recommendations": [],
        }

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    # ── Build spending context ────────────────────────────────────────────────
    expenses = df[df["amount"] < 0].copy()
    expenses["amount_abs"] = expenses["amount"].abs()

    # Current month stats
    today = datetime.now()
    days_elapsed = today.day
    days_in_month = 30  # approximation

    try:
        expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
        current_month_exp = expenses[
            (expenses["date"].dt.month == today.month) &
            (expenses["date"].dt.year == today.year)
        ]
    except Exception:
        current_month_exp = expenses

    cat_actual = (
        current_month_exp.groupby("category")["amount_abs"].sum().to_dict()
        if not current_month_exp.empty
        else expenses.groupby("category")["amount_abs"].sum().to_dict()
    )

    # All-time category totals for pattern detection
    cat_alltime = expenses.groupby("category")["amount_abs"].sum().to_dict()

    # Budget map
    budget_map = {b["category"]: float(b["monthly_limit"]) for b in budgets}

    # Recent transactions list (last 20)
    recent_txns = (
        df.sort_values("date", ascending=False)
        .head(20)[["date", "description", "amount", "category"]]
        .to_string(index=False)
    )

    # Recurring merchant detection
    desc_counts = expenses["description"].value_counts().head(10).to_dict()
    recurring = [f"{k} (×{v})" for k, v in desc_counts.items()]

    budget_lines = "\n".join(
        f"  {cat}: spent ${cat_actual.get(cat, 0):.2f} / budget ${lim:.2f}"
        for cat, lim in budget_map.items()
    ) if budget_map else "  No budgets set yet."

    context = f"""
Today: {today.strftime('%B %d, %Y')} (day {days_elapsed} of {days_in_month})
Total transactions: {len(transactions)}
Total expenses (all time): ${sum(cat_alltime.values()):.2f}

This month — Actual vs Budget:
{budget_lines}

Recurring merchants (all time):
  {', '.join(recurring) if recurring else 'None detected'}

Last 20 transactions:
{recent_txns}
"""

    prompt = f"""You are a personal finance AI that gives sharp, specific insights.

Analyse the spending data below and return a JSON object with EXACTLY these keys:

{{
  "summary": "<2-3 sentence plain-English summary of spending health>",
  "health_score": <integer 0-100; 100=perfectly on budget, 0=severely over>,
  "alerts": [
    {{
      "category": "<category name>",
      "message": "<specific alert, e.g. '85% of budget used with 12 days left'>",
      "severity": "high|medium|low"
    }}
  ],
  "predictions": [
    {{
      "category": "<category>",
      "spent_so_far": <number>,
      "predicted_monthly_total": <number>,
      "budget": <number or null>,
      "will_exceed": <true|false>,
      "reason": "<short reason for prediction>"
    }}
  ],
  "recommendations": [
    {{
      "title": "<specific actionable title, e.g. 'Skip the cinema this weekend'>",
      "detail": "<1-2 sentences with specific context from their actual transactions>",
      "estimated_savings": <number>,
      "category": "<category>"
    }}
  ]
}}

RULES:
- Be SPECIFIC — reference actual merchants, amounts, and patterns from the data.
- Recommendations must be concrete (e.g. "You visited Starbucks 8 times this month — switching to home coffee saves ~$32").
- If no budgets are set, still generate predictions and recommendations from spending patterns alone.
- Output ONLY the JSON object. No markdown, no explanation.

Spending data:
{context}

JSON:"""

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.4),
        )
        raw = response.text
    except Exception as exc:
        raise RuntimeError(f"Gemini insights call failed: {exc}") from exc

    cleaned = _strip_fences(raw)
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: return a basic structure
        return {
            "summary": raw[:300],
            "health_score": 50,
            "alerts": [],
            "predictions": [],
            "recommendations": [],
        }

    return result


# ─── 3. Budget Suggestions ────────────────────────────────────────────────────

def suggest_budgets(transactions: list[dict]) -> list[dict]:
    """
    Analyse historical spending and suggest realistic monthly budget limits.
    Returns list of {category, suggested_limit, reasoning}.
    """
    import google.generativeai as genai
    import pandas as pd

    if not transactions:
        return []

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    expenses = df[df["amount"] < 0].copy()
    expenses["amount_abs"] = expenses["amount"].abs()

    cat_avg = expenses.groupby("category")["amount_abs"].sum()

    # Estimate how many months of data we have
    try:
        expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
        date_range = (expenses["date"].max() - expenses["date"].min()).days
        months = max(1, round(date_range / 30))
    except Exception:
        months = 1

    monthly_avgs = (cat_avg / months).round(2).to_dict()
    avg_lines = "\n".join(f"  {cat}: ${amt:.2f}/month avg" for cat, amt in monthly_avgs.items())

    prompt = f"""Based on this user's average monthly spending by category, suggest realistic monthly budget limits.

Average monthly spending:
{avg_lines}

Return a JSON array:
[
  {{
    "category": "<category>",
    "suggested_limit": <number — slightly above average to be realistic but encourage saving>,
    "reasoning": "<one sentence explaining the suggestion>"
  }}
]

Output ONLY the JSON array. No markdown or explanation."""

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2),
        )
        data = json.loads(_strip_fences(response.text))
        return data if isinstance(data, list) else []
    except Exception:
        return []


# ─── 4. Follow-up Chat ────────────────────────────────────────────────────────

def answer_finance_question(
    question: str,
    transactions: list[dict],
    chat_history: list[dict] | None = None,
) -> str:
    import google.generativeai as genai
    import pandas as pd

    if not transactions:
        return "No transactions found yet. Upload a bank statement from the Dashboard first."

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    total_spent  = df[df["amount"] < 0]["amount"].sum()
    total_income = df[df["amount"] > 0]["amount"].sum()
    cat_totals   = (
        df[df["amount"] < 0].groupby("category")["amount"].sum().abs()
        .sort_values(ascending=False).to_dict()
    )
    cat_lines  = "\n".join(f"  • {c}: ${a:,.2f}" for c, a in cat_totals.items())
    recent     = df.head(10)[["date", "description", "amount", "category"]].to_string(index=False)

    history_str = ""
    if chat_history:
        lines = [
            f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
            for m in chat_history[-6:]
        ]
        history_str = "\n".join(lines) + "\n"

    prompt = f"""You are a concise personal finance advisor.

Financial summary:
  Total transactions : {len(transactions)}
  Total income       : ${total_income:,.2f}
  Total expenses     : ${abs(total_spent):,.2f}
  Net                : ${(total_income + total_spent):,.2f}

By category:
{cat_lines}

Recent 10 transactions:
{recent}

{history_str}User: {question}
Assistant:"""

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7),
        )
        return response.text.strip()
    except Exception as exc:
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc
