"""
Supabase client — Auth + DB queries.

Required Supabase SQL (run once in the SQL Editor):
─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date        DATE,
    description TEXT,
    amount      NUMERIC(12, 2),
    category    TEXT,
    source_file TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS budgets (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category      TEXT        NOT NULL,
    monthly_limit NUMERIC(12, 2) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, category)
);

-- Enable Row Level Security (strongly recommended for production)
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets      ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own transactions"
    ON transactions FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users see own budgets"
    ON budgets FOR ALL USING (auth.uid() = user_id);
─────────────────────────────────────────────────────
"""

import os
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        "SUPABASE_URL and SUPABASE_KEY must be set in your .env file."
    )

_client: Optional[Client] = None


def get_client() -> Client:
    """Return a singleton Supabase client."""
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ─── Authentication ───────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> dict:
    """
    Register a new user.
    Returns {"user": ..., "session": ..., "error": str|None}.
    """
    try:
        response = get_client().auth.sign_up({"email": email, "password": password})
        return {"user": response.user, "session": response.session, "error": None}
    except Exception as exc:
        return {"user": None, "session": None, "error": str(exc)}


def sign_in(email: str, password: str) -> dict:
    """
    Sign in with email + password.
    Returns {"user": ..., "session": ..., "error": str|None}.
    """
    try:
        response = get_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return {"user": response.user, "session": response.session, "error": None}
    except Exception as exc:
        return {"user": None, "session": None, "error": str(exc)}


def sign_out() -> None:
    """Sign out the current user."""
    try:
        get_client().auth.sign_out()
    except Exception:
        pass


# ─── Transactions ─────────────────────────────────────────────────────────────

def insert_transactions(user_id: str, transactions: list[dict], source_file: str = "") -> dict:
    """
    Bulk-insert a list of transaction dicts for the given user.

    Each dict must contain: date, description, amount, category.
    Returns {"data": [...], "error": str|None}.
    """
    if not transactions:
        return {"data": [], "error": None}

    rows = [
        {
            "user_id":     user_id,
            "date":        t.get("date"),
            "description": t.get("description", ""),
            "amount":      float(t.get("amount", 0)),
            "category":    t.get("category", "Other"),
            "source_file": source_file,
        }
        for t in transactions
    ]

    try:
        result = get_client().table("transactions").insert(rows).execute()
        return {"data": result.data, "error": None}
    except Exception as exc:
        return {"data": [], "error": str(exc)}


def fetch_transactions(user_id: str) -> dict:
    """
    Fetch all transactions belonging to the user, newest first.
    Returns {"data": [...], "error": str|None}.
    """
    try:
        result = (
            get_client()
            .table("transactions")
            .select("*")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .execute()
        )
        return {"data": result.data, "error": None}
    except Exception as exc:
        return {"data": [], "error": str(exc)}


def delete_transactions(user_id: str) -> dict:
    """Delete ALL transactions for a user (used for 'reset data')."""
    try:
        result = (
            get_client()
            .table("transactions")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )
        return {"data": result.data, "error": None}
    except Exception as exc:
        return {"data": [], "error": str(exc)}


# ─── Budgets ──────────────────────────────────────────────────────────────────

def upsert_budget(user_id: str, category: str, monthly_limit: float) -> dict:
    """Create or update a budget limit for a category."""
    try:
        result = (
            get_client()
            .table("budgets")
            .upsert(
                {"user_id": user_id, "category": category, "monthly_limit": monthly_limit},
                on_conflict="user_id,category",
            )
            .execute()
        )
        return {"data": result.data, "error": None}
    except Exception as exc:
        return {"data": [], "error": str(exc)}


def fetch_budgets(user_id: str) -> dict:
    """Fetch all budget limits for a user."""
    try:
        result = (
            get_client()
            .table("budgets")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return {"data": result.data, "error": None}
    except Exception as exc:
        return {"data": [], "error": str(exc)}
