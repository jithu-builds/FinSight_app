# AI Personal Finance Tracker — Initial Setup

## Before You Run — One-Time Setup

### 1. Fill in `.env`

Open the `.env` file in the project root and add your real credentials:

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=your-gemini-key
REDUCTO_API_KEY=your-reducto-key
```

### 2. Run SQL in Supabase

Open your **Supabase project → SQL Editor** and run the full schema script found at the top of `backend/supabase_client.py`. It creates:

- `transactions` table — stores parsed bank statement rows per user
- `budgets` table — stores monthly category limits per user
- Row Level Security (RLS) policies — ensures users can only access their own data

```sql
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

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets      ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own transactions"
    ON transactions FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users see own budgets"
    ON budgets FOR ALL USING (auth.uid() = user_id);
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Disable Email Confirmation

In your Supabase project go to **Authentication → Providers → Email** and disable **Confirm email** for easier local development. Re-enable it before going to production.

### 5. Start the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Key Design Decisions

| Concern | Approach |
|---|---|
| Auth guard | `app.py` checks `st.session_state.logged_in` before rendering any page |
| Data isolation | Every DB insert/query filters on `user_id`; RLS SQL adds a second layer |
| Reducto errors | Wrapped in specific `RuntimeError` messages — empty response, bad upload ID, and attribute errors all surface clearly |
| Gemini JSON | `_strip_markdown_fences()` removes ` ```json ``` ` wrappers Gemini sometimes adds before `json.loads()` |
| PDF reprocess guard | `last_uploaded_file` key prevents re-running the pipeline on every Streamlit rerun |
| Chat context | Last 3 conversation turns + full transaction summary injected into every Gemini prompt |
