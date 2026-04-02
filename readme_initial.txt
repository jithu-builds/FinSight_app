================================================================================
  AI PERSONAL FINANCE TRACKER — INITIAL SETUP
================================================================================

Before running the app for the first time, complete the following four steps.


--------------------------------------------------------------------------------
  STEP 1 — FILL IN YOUR API KEYS
--------------------------------------------------------------------------------

Open the .env file in the project root and add your credentials:

    SUPABASE_URL     = https://xxxx.supabase.co
    SUPABASE_KEY     = your-anon-key
    GEMINI_API_KEY   = your-gemini-key
    REDUCTO_API_KEY  = your-reducto-key


--------------------------------------------------------------------------------
  STEP 2 — CREATE THE DATABASE TABLES IN SUPABASE
--------------------------------------------------------------------------------

Go to your Supabase project → SQL Editor and run the script located at the
top of backend/supabase_client.py.

It will create the following:

  • transactions table
    Stores parsed bank statement rows, linked to each user.
    Columns: id, user_id, date, description, amount, category,
             source_file, created_at

  • budgets table
    Stores monthly spending limits per category, per user.
    Columns: id, user_id, category, monthly_limit, created_at

  • Row Level Security (RLS) policies
    Ensures every user can only read and write their own data.
    (Strongly recommended — do not skip for production.)


--------------------------------------------------------------------------------
  STEP 3 — INSTALL DEPENDENCIES
--------------------------------------------------------------------------------

Run the following command from the project root:

    pip install -r requirements.txt


--------------------------------------------------------------------------------
  STEP 4 — (OPTIONAL) DISABLE EMAIL CONFIRMATION FOR LOCAL DEV
--------------------------------------------------------------------------------

In Supabase go to:
  Authentication → Providers → Email → Disable "Confirm email"

This lets you sign up and log in instantly without checking your inbox.
Re-enable it before deploying to production.


--------------------------------------------------------------------------------
  STEP 5 — START THE APP
--------------------------------------------------------------------------------

    streamlit run app.py

The app will open at:  http://localhost:8501


================================================================================
  KEY DESIGN DECISIONS
================================================================================

  Auth Guard
    app.py checks st.session_state.logged_in before rendering any page.
    Unauthenticated users only ever see the Login / Sign-Up screen.

  Data Isolation
    Every database insert and query is filtered by user_id.
    Supabase RLS policies enforce this at the database level as well.

  Reducto Error Handling
    The PDF parser surfaces specific errors for: empty responses,
    missing upload IDs, and unexpected response structures.

  Gemini JSON Safety
    A cleanup step strips any markdown code fences (```json ... ```)
    that Gemini sometimes wraps around its output before JSON parsing.

  PDF Reprocess Guard
    A session state key (last_uploaded_file) prevents the processing
    pipeline from re-running on every Streamlit rerun.

  Chat Context
    Each Gemini chat request includes the last 3 conversation turns
    plus a full spending summary built from the user's transactions.


================================================================================
  FILE STRUCTURE
================================================================================

  app.py                          Main entry point and page router
  requirements.txt                Python dependencies
  .env                            API keys (never commit this file)

  components/
    auth.py                       Login / Signup UI and session state

  frontend/
    dashboard.py                  PDF upload, spending charts, transaction table
    budgeting.py                  Budget limits vs actual spending tracker
    chat_ai.py                    Conversational AI advisor (Gemini)

  backend/
    supabase_client.py            Auth functions and all database queries
    document_parser.py            Reducto API — PDF to Markdown extraction
    ai_engine.py                  Gemini — transaction extraction and chat

================================================================================
