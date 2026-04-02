"""
Authentication UI component.

Manages Login / Sign-Up flows and writes the following keys to
st.session_state upon success:

    st.session_state.logged_in    → bool
    st.session_state.user_id      → str   (Supabase auth.users UUID)
    st.session_state.user_email   → str
    st.session_state.access_token → str   (JWT — for future RLS use)
"""

import streamlit as st

from backend.supabase_client import sign_in, sign_up, sign_out


def _init_session() -> None:
    defaults = {
        "logged_in":    False,
        "user_id":      None,
        "user_email":   None,
        "access_token": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _handle_sign_in(email: str, password: str) -> None:
    if not email or not password:
        st.error("Please enter both email and password.")
        return

    with st.spinner("Signing in…"):
        result = sign_in(email, password)

    if result["error"]:
        st.error(f"Login failed: {result['error']}")
        return

    user = result["user"]
    session = result["session"]

    st.session_state.logged_in    = True
    st.session_state.user_id      = str(user.id)
    st.session_state.user_email   = user.email
    st.session_state.access_token = session.access_token if session else ""
    st.rerun()


def _handle_sign_up(email: str, password: str, confirm: str) -> None:
    if not email or not password or not confirm:
        st.error("All fields are required.")
        return

    if password != confirm:
        st.error("Passwords do not match.")
        return

    if len(password) < 6:
        st.error("Password must be at least 6 characters.")
        return

    with st.spinner("Creating account…"):
        result = sign_up(email, password)

    if result["error"]:
        st.error(f"Sign-up failed: {result['error']}")
        return

    # Supabase may require email confirmation depending on project settings.
    if result["session"] is None:
        st.success(
            "Account created! Check your email for a confirmation link, "
            "then come back to log in."
        )
    else:
        user    = result["user"]
        session = result["session"]
        st.session_state.logged_in    = True
        st.session_state.user_id      = str(user.id)
        st.session_state.user_email   = user.email
        st.session_state.access_token = session.access_token
        st.rerun()


def logout() -> None:
    """Call this from the main app to log the user out."""
    sign_out()
    for key in ("logged_in", "user_id", "user_email", "access_token"):
        st.session_state[key] = None if key != "logged_in" else False
    # Also clear any cached app data
    for key in ("transactions", "chat_messages"):
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def show_auth_page() -> None:
    """
    Render the full-screen authentication page.
    Call this from app.py when the user is NOT logged in.
    """
    _init_session()

    st.markdown(
        """
        <h1 style='text-align:center; margin-bottom:0'>
            💰 AI Finance Tracker
        </h1>
        <p style='text-align:center; color:grey; margin-top:4px'>
            Your personal spending intelligence
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

        # ── Login tab ──────────────────────────────────────────────────────────
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                _handle_sign_in(email, password)

        # ── Sign-up tab ────────────────────────────────────────────────────────
        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                email    = st.text_input("Email", placeholder="you@example.com", key="su_email")
                password = st.text_input("Password", type="password", key="su_pass")
                confirm  = st.text_input("Confirm Password", type="password", key="su_confirm")
                submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                _handle_sign_up(email, password, confirm)
