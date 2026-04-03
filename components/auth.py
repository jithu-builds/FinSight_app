"""
Authentication UI — login/signup + cookie-based session persistence.

Session survives browser refresh by storing user_id, user_email, and
access_token in browser cookies via extra-streamlit-components.

st.session_state keys written on success:
    logged_in    → bool
    user_id      → str
    user_email   → str
    access_token → str
"""

from datetime import datetime, timedelta

import streamlit as st
from components.session_store import get_cm as _cm

from backend.supabase_client import sign_in, sign_up, sign_out


COOKIE_EXPIRY = datetime.now() + timedelta(days=7)
COOKIE_KEYS   = ("ft_user_id", "ft_user_email", "ft_access_token")


# ─── Cookie helpers ───────────────────────────────────────────────────────────

def save_session_to_cookies(user_id: str, email: str, token: str) -> None:
    cm = _cm()
    cm.set("ft_user_id",      user_id, expires_at=COOKIE_EXPIRY)
    cm.set("ft_user_email",   email,   expires_at=COOKIE_EXPIRY)
    cm.set("ft_access_token", token,   expires_at=COOKIE_EXPIRY)


def restore_session_from_cookies() -> bool:
    """
    Try to restore session from cookies.
    Returns True if session was successfully restored.
    """
    if st.session_state.get("logged_in"):
        return True

    cm = _cm()
    user_id = cm.get("ft_user_id")
    email   = cm.get("ft_user_email")
    token   = cm.get("ft_access_token")

    if user_id and email and token:
        st.session_state.logged_in    = True
        st.session_state.user_id      = user_id
        st.session_state.user_email   = email
        st.session_state.access_token = token
        return True

    return False


def clear_session_cookies() -> None:
    cm = _cm()
    for key in COOKIE_KEYS:
        try:
            cm.delete(key)
        except Exception:
            pass


# ─── Session state init ───────────────────────────────────────────────────────

def _init_session() -> None:
    for key, val in {
        "logged_in": False, "user_id": None,
        "user_email": None, "access_token": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _persist_session(result: dict) -> None:
    user    = result["user"]
    session = result["session"]
    token   = session.access_token if session else ""

    st.session_state.logged_in    = True
    st.session_state.user_id      = str(user.id)
    st.session_state.user_email   = user.email
    st.session_state.access_token = token

    save_session_to_cookies(str(user.id), user.email, token)


# ─── Logout ───────────────────────────────────────────────────────────────────

def logout() -> None:
    sign_out()
    clear_session_cookies()
    for key in ("logged_in", "user_id", "user_email", "access_token",
                "transactions", "chat_messages", "last_uploaded_file"):
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.logged_in = False
    st.rerun()


# ─── Form handlers ────────────────────────────────────────────────────────────

def _handle_sign_in(email: str, password: str) -> None:
    if not email or not password:
        st.error("Please enter both email and password.")
        return
    with st.spinner("Signing in…"):
        result = sign_in(email, password)
    if result["error"]:
        st.error(f"Login failed — {result['error']}")
        return
    _persist_session(result)
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
    with st.spinner("Creating your account…"):
        result = sign_up(email, password)
    if result["error"]:
        st.error(f"Sign-up failed — {result['error']}")
        return
    if result["session"] is None:
        st.success("Account created! Check your inbox to confirm, then log in.")
    else:
        _persist_session(result)
        st.rerun()


# ─── Auth CSS ─────────────────────────────────────────────────────────────────

AUTH_CSS = """
<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1040 50%, #0f172a 100%); min-height: 100vh; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }

.auth-card {
    background: rgba(255,255,255,0.04); backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.09); border-radius: 24px;
    padding: 2.5rem 2.5rem 2rem; box-shadow: 0 25px 50px rgba(0,0,0,0.5);
}
.auth-logo { text-align:center; margin-bottom:0.25rem; }
.auth-logo .icon { font-size:3rem; line-height:1; }
.auth-logo h1 { font-size:1.75rem; font-weight:700; color:#f1f5f9; margin:0.35rem 0 0.2rem; letter-spacing:-0.5px; }
.auth-logo p { color:#94a3b8; font-size:0.875rem; margin:0; }
.auth-divider { height:1px; background:linear-gradient(to right,transparent,rgba(255,255,255,0.1),transparent); margin:1.5rem 0; }

.stTabs [data-baseweb="tab-list"] { background:rgba(255,255,255,0.04) !important; border-radius:12px !important; padding:4px !important; gap:4px !important; border:1px solid rgba(255,255,255,0.07) !important; }
.stTabs [data-baseweb="tab"] { border-radius:9px !important; color:#94a3b8 !important; font-weight:500 !important; font-size:0.9rem !important; padding:0.5rem 1.25rem !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#6366f1,#818cf8) !important; color:#fff !important; box-shadow:0 4px 12px rgba(99,102,241,0.4) !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none !important; }

.stTextInput label { color:#94a3b8 !important; font-size:0.8rem !important; font-weight:600 !important; text-transform:uppercase !important; letter-spacing:0.08em !important; }
.stTextInput input { background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.1) !important; border-radius:10px !important; color:#f1f5f9 !important; }
.stTextInput input:focus { border-color:#6366f1 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.2) !important; }

.stFormSubmitButton button { background:linear-gradient(135deg,#6366f1,#818cf8) !important; color:#fff !important; border:none !important; border-radius:10px !important; font-weight:600 !important; box-shadow:0 4px 15px rgba(99,102,241,0.4) !important; }
.stFormSubmitButton button:hover { opacity:0.9 !important; transform:translateY(-1px) !important; }
</style>
"""


# ─── Auth page ────────────────────────────────────────────────────────────────

def show_auth_page() -> None:
    _init_session()
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        st.markdown(
            """
            <div class="auth-card">
              <div class="auth-logo">
                <div class="icon">💰</div>
                <h1>Finance Tracker</h1>
                <p>Your personal spending intelligence</p>
              </div>
              <div class="auth-divider"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["  Log In  ", "  Sign Up  "])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                email    = st.text_input("Email",    placeholder="you@example.com")
                password = st.text_input("Password", placeholder="••••••••", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Log In →", use_container_width=True)
            if submitted:
                _handle_sign_in(email, password)

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form"):
                email   = st.text_input("Email",            placeholder="you@example.com", key="su_email")
                pw      = st.text_input("Password",         placeholder="Min. 6 characters", type="password", key="su_pass")
                confirm = st.text_input("Confirm Password", placeholder="Repeat password",   type="password", key="su_confirm")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Create Account →", use_container_width=True)
            if submitted:
                _handle_sign_up(email, pw, confirm)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align:center;color:#475569;font-size:0.75rem'>"
            "Secured by Supabase Auth · Data never shared</p>",
            unsafe_allow_html=True,
        )
