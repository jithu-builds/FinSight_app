"""
Authentication UI — dialog-based login/signup + cookie-based session persistence.

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

from backend.supabase_client import sign_in, sign_up, sign_out, reset_password


COOKIE_EXPIRY = datetime.now() + timedelta(days=7)
COOKIE_KEYS   = ("ft_user_id", "ft_user_email", "ft_access_token")


# ─── Cookie helpers ───────────────────────────────────────────────────────────

def save_session_to_cookies(user_id: str, email: str, token: str) -> None:
    cm = _cm()
    cm.set("ft_user_id",      user_id, expires_at=COOKIE_EXPIRY)
    cm.set("ft_user_email",   email,   expires_at=COOKIE_EXPIRY)
    cm.set("ft_access_token", token,   expires_at=COOKIE_EXPIRY)


def restore_session_from_cookies() -> bool:
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


def _handle_reset(email: str) -> None:
    if not email:
        st.error("Please enter your email address.")
        return
    with st.spinner("Sending reset link…"):
        result = reset_password(email)
    if result["error"]:
        st.error(f"Could not send reset email — {result['error']}")
        return
    st.success("✅ Password reset link sent! Check your inbox.")


# ─── Dialog CSS (injected inside the dialog) ─────────────────────────────────

_DIALOG_CSS = """
<style>
/* Style the Streamlit dialog backdrop and card */
[data-testid="stDialog"] > div {
    background: rgba(0,0,0,0.65) !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="stDialog"] [data-testid="stModalDialog"] {
    background: #0e1420 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 20px !important;
    box-shadow: 0 40px 80px rgba(0,0,0,0.7) !important;
}
/* Top shimmer line on dialog card */
[data-testid="stDialog"] [data-testid="stModalDialog"]::before {
    content: '';
    position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), transparent);
}
/* Dialog title hidden — we render our own header */
[data-testid="stDialog"] h2 { display: none !important; }

.auth-dialog-logo {
    text-align: center; padding: 0.5rem 0 1rem;
}
.auth-dialog-logo .icon {
    font-size: 2.2rem; display: block; margin-bottom: 0.4rem;
    filter: drop-shadow(0 0 18px rgba(99,102,241,0.65));
}
.auth-dialog-logo h3 {
    font-size: 1.5rem !important; font-weight: 800 !important;
    color: #e2e8f0 !important; letter-spacing: -0.5px !important;
    margin: 0 0 0.1rem !important;
}
.auth-dialog-logo .sub {
    font-size: 0.65rem; color: #475569; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.16em;
}
.auth-divider {
    height: 1px; margin: 0.75rem 0 1rem;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.06), transparent);
}
.auth-reset-link {
    text-align: right; margin-top: -0.25rem; margin-bottom: 0.75rem;
}
.auth-reset-link a {
    font-size: 0.78rem; color: #5d6a82; text-decoration: none;
    cursor: pointer; transition: color 0.15s;
}
.auth-reset-link a:hover { color: #c7d2fe; }
.auth-footer {
    text-align: center; margin-top: 0.75rem;
    font-size: 0.72rem; color: #334155;
}
</style>
"""


# ─── Auth dialog ──────────────────────────────────────────────────────────────

@st.dialog("FinSight", width="small")
def show_auth_dialog() -> None:
    _init_session()
    st.markdown(_DIALOG_CSS, unsafe_allow_html=True)

    # Brand header
    st.markdown(
        """
        <div class="auth-dialog-logo">
            <span class="icon">💡</span>
            <h3>FinSight</h3>
            <div class="sub">AI Finance Tracker</div>
        </div>
        <div class="auth-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    # ── Reset password mode ────────────────────────────────────────────────────
    if st.session_state.get("auth_mode") == "reset":
        st.markdown(
            "<p style='font-size:0.85rem;color:#5d6a82;font-family:Inter,sans-serif;"
            "margin-bottom:1rem'>Enter your email and we'll send you a reset link.</p>",
            unsafe_allow_html=True,
        )
        with st.form("reset_form"):
            email     = st.text_input("Email", placeholder="you@example.com", key="reset_email")
            submitted = st.form_submit_button("Send Reset Link →", use_container_width=True)
        if submitted:
            _handle_reset(email)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("← Back to Log In", key="back_to_login", use_container_width=False):
            st.session_state.auth_mode = "login"
            st.rerun()

        st.markdown(
            "<div class='auth-footer'>🔒 Secured by Supabase Auth · Data never shared</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Normal mode: Log In / Sign Up tabs ────────────────────────────────────
    tab_login, tab_signup = st.tabs(["  Log In  ", "  Sign Up  "])

    with tab_login:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            email    = st.text_input("Email",    placeholder="you@example.com", key="li_email")
            password = st.text_input("Password", placeholder="••••••••", type="password", key="li_pass")
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Log In →", use_container_width=True)
        if submitted:
            _handle_sign_in(email, password)

        # Forgot password — styled as a subtle text link
        st.markdown(
            """
            <style>
            [data-testid="stDialog"] button[kind="secondary"]:has(+ *),
            div[data-testid="stDialog"] .forgot-btn button {
                background: none !important; border: none !important;
                box-shadow: none !important; color: #5d6a82 !important;
                font-size: 0.78rem !important; font-weight: 400 !important;
                padding: 0 !important; text-decoration: underline !important;
                text-underline-offset: 3px !important;
            }
            div[data-testid="stDialog"] .forgot-btn button:hover {
                color: #c4b5fd !important; transform: none !important;
                box-shadow: none !important;
            }
            </style>
            <div class="forgot-btn">
            """,
            unsafe_allow_html=True,
        )
        if st.button("Forgot password?", key="forgot_pw"):
            st.session_state.auth_mode = "reset"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_signup:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        with st.form("signup_form"):
            email   = st.text_input("Email",            placeholder="you@example.com",   key="su_email")
            pw      = st.text_input("Password",         placeholder="Min. 6 characters", type="password", key="su_pass")
            confirm = st.text_input("Confirm Password", placeholder="Repeat password",   type="password", key="su_confirm")
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account →", use_container_width=True)
        if submitted:
            _handle_sign_up(email, pw, confirm)

    st.markdown(
        "<div class='auth-footer'>🔒 Secured by Supabase Auth · Data never shared</div>",
        unsafe_allow_html=True,
    )
