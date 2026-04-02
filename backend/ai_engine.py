"""
Google Gemini AI engine.

Two responsibilities:
  1. extract_transactions_from_markdown()
     → Parses raw bank-statement Markdown into a clean JSON transaction list.

  2. answer_finance_question()
     → Answers a user's natural-language question about their spending data.
"""

import json
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set. Add it to your .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)

_MODEL_NAME = "gemini-1.5-flash"

VALID_CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Rent & Housing",
    "Healthcare",
    "Income",
    "Transfer",
    "Subscriptions",
    "Other",
]


def _get_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(_MODEL_NAME)


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers that Gemini sometimes adds."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


# ─── Transaction Extraction ───────────────────────────────────────────────────

def extract_transactions_from_markdown(markdown_text: str) -> list[dict]:
    """
    Send bank-statement Markdown to Gemini and return a list of transaction
    dicts: [{date, description, amount, category}, ...].

    Raises:
        RuntimeError  – Gemini call failed or returned unparseable JSON.
        ValueError    – The parsed response is not a JSON array.
    """
    categories_str = ", ".join(VALID_CATEGORIES)

    prompt = f"""You are a financial data extraction assistant.

Carefully read the bank statement text below and extract EVERY transaction.

For each transaction output these four fields:
  - "date"        : transaction date in ISO format YYYY-MM-DD (best guess if partial)
  - "description" : merchant or payee name, cleaned and concise (max 60 chars)
  - "amount"      : numeric value; NEGATIVE for debits/expenses, POSITIVE for credits/income
  - "category"    : assign exactly one category from this list:
                    {categories_str}

STRICT OUTPUT RULES:
  1. Output ONLY a valid JSON array — no markdown, no explanation, no extra text.
  2. Every object must have all four keys.
  3. If a field cannot be determined, use null for date/description and 0 for amount.
  4. Do NOT wrap the array in a code fence or any other formatting.

Example of valid output (structure only):
[
  {{"date": "2024-03-15", "description": "Starbucks Coffee", "amount": -4.75, "category": "Food & Dining"}},
  {{"date": "2024-03-16", "description": "Employer Payroll", "amount": 2450.00, "category": "Income"}}
]

Bank statement text:
─────────────────────────────────────────────────────────────────
{markdown_text}
─────────────────────────────────────────────────────────────────

JSON array:"""

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1),
        )
        raw_text = response.text
    except Exception as exc:
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

    cleaned = _strip_markdown_fences(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemini returned invalid JSON.\n"
            f"Parse error: {exc}\n"
            f"Raw response (first 500 chars): {cleaned[:500]}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array from Gemini, got {type(data).__name__}."
        )

    # Basic sanitisation: ensure numeric amounts
    for txn in data:
        try:
            txn["amount"] = float(txn.get("amount") or 0)
        except (TypeError, ValueError):
            txn["amount"] = 0.0

    return data


# ─── Finance Advisor Chat ─────────────────────────────────────────────────────

def answer_finance_question(
    question: str,
    transactions: list[dict],
    chat_history: list[dict] | None = None,
) -> str:
    """
    Answer a natural-language question about the user's spending data.

    Args:
        question      : The user's current question.
        transactions  : Full list of user transaction dicts from Supabase.
        chat_history  : Optional list of {"role": "user"|"assistant", "content": str}
                        for maintaining conversational context.

    Returns:
        The assistant's answer as a plain string.

    Raises:
        RuntimeError  – Gemini API failure.
    """
    if not transactions:
        return (
            "I don't see any transactions in your account yet. "
            "Please upload a bank statement PDF from the Dashboard first."
        )

    # Build a compact spending summary to keep the prompt concise
    from collections import defaultdict
    import pandas as pd

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    total_spent = df[df["amount"] < 0]["amount"].sum()
    total_income = df[df["amount"] > 0]["amount"].sum()

    category_totals = (
        df[df["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .to_dict()
    )

    cat_lines = "\n".join(
        f"  • {cat}: ${amt:,.2f}" for cat, amt in category_totals.items()
    )

    recent = df.head(10)[["date", "description", "amount", "category"]].to_string(index=False)

    spending_context = f"""
User's Financial Summary
─────────────────────────
Total transactions : {len(transactions)}
Total income       : ${total_income:,.2f}
Total expenses     : ${abs(total_spent):,.2f}
Net                : ${(total_income + total_spent):,.2f}

Spending by category:
{cat_lines}

10 most recent transactions:
{recent}
─────────────────────────"""

    # Build conversation history string
    history_str = ""
    if chat_history:
        history_lines = []
        for msg in chat_history[-6:]:  # last 3 turns for context
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['content']}")
        history_str = "\n".join(history_lines) + "\n"

    prompt = f"""You are a helpful, concise personal finance advisor.
You have access to the user's real transaction data shown below.
Answer in a friendly, actionable tone. Keep responses under 250 words unless a detailed breakdown is asked for.

{spending_context}

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
