"""
FinSight — AI Personal Finance Tracker · Streamlit entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st
import extra_streamlit_components as stx
from components.session_store import set_cm

st.set_page_config(
    page_title="FinSight",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Create CookieManager ONCE per render and register it in the shared store.
set_cm(stx.CookieManager(key="finsight_cookies"))

# ─── Global CSS ───────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Base ── */
.stApp {
    background: #080d1a;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1120 0%, #080d1a 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
[data-testid="stSidebar"] .stRadio label {
    display: flex; align-items: center; justify-content: center;
    padding: 0.75rem 1.1rem; border-radius: 12px;
    color: #64748b !important; font-weight: 600; font-size: 1.05rem;
    cursor: pointer; transition: background 0.15s, color 0.15s;
    margin-bottom: 4px; border-left: none; text-align: center;
    gap: 0;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(99,102,241,0.1); color: #c7d2fe !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(20,184,166,0.08)) !important;
    color: #a5b4fc !important;
    box-shadow: inset 0 0 0 1px rgba(99,102,241,0.35) !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] {
    width: 100%; text-align: center;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    margin: 0; line-height: 1.3; text-align: center;
}
/* Hide radio dot/circle indicators completely */
[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio label > div:first-child { display: none !important; }
/* Hide the "nav" widget label that appears above the navigation items */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] .stRadio > label { display: none !important; }

/* ── Content area ── */
.block-container { padding: 1.75rem 2.5rem 2rem !important; max-width: 1400px; }

/* ── Typography ── */
h1 {
    font-size: 1.75rem !important; font-weight: 800 !important;
    color: #f1f5f9 !important; letter-spacing: -0.5px !important;
    margin-bottom: 0.25rem !important;
}
h2 { font-size: 1.2rem !important; font-weight: 700 !important; color: #e2e8f0 !important; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: #cbd5e1 !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #111827; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.2rem 1.4rem !important;
    transition: border-color 0.2s, transform 0.2s;
}
[data-testid="stMetric"]:hover { border-color: rgba(99,102,241,0.3); transform: translateY(-1px); }
[data-testid="stMetricLabel"] {
    color: #475569 !important; font-size: 0.75rem !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    color: #f1f5f9 !important; font-size: 1.65rem !important;
    font-weight: 800 !important; letter-spacing: -0.5px !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

/* ── Buttons ── */
.stButton button, .stFormSubmitButton button {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 0.875rem !important;
    padding: 0.55rem 1.3rem !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    opacity: 0.88 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: rgba(239,68,68,0.1) !important; color: #f87171 !important;
    box-shadow: none !important; border: 1px solid rgba(239,68,68,0.2) !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(239,68,68,0.2) !important;
    transform: none !important; box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput label, .stNumberInput label, .stSelectbox label {
    color: #475569 !important; font-size: 0.75rem !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}
.stTextInput input, .stNumberInput input {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}
div[data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #111827 !important;
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 16px !important; padding: 1rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(99,102,241,0.6) !important; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important; overflow: hidden !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111827 !important; border-radius: 14px !important;
    padding: 5px !important; gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important; color: #475569 !important;
    font-weight: 600 !important; padding: 0.45rem 1.2rem !important;
    font-size: 0.875rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
    color: #fff !important; box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
}

/* ── Dividers ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important; padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stChatInputTextArea"] {
    background: #111827 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important; color: #f1f5f9 !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 12px !important; border: none !important; font-size: 0.875rem !important; }

/* ── Spinner ── */
.stSpinner [data-testid="stSpinner"] div,
div[data-testid="stSpinner"] > div > div { border-top-color: #818cf8 !important; }

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #6366f1, #14b8a6) !important;
    border-radius: 99px !important;
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Full-screen loading overlay ────────────────────────────────────────────────
_loader = st.empty()
_loader.markdown(
    """
    <style>
    #fs-loader {
        position: fixed; inset: 0; background: #080d1a;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        gap: 0.75rem; z-index: 99999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .fsl-icon  { font-size: 3.5rem; animation: fsl-pulse 1.6s ease-in-out infinite; }
    .fsl-title { color: #f1f5f9; font-size: 1.65rem; font-weight: 800;
                 letter-spacing: -0.5px; margin: 0.25rem 0 0; }
    .fsl-sub   { color: #334155; font-size: 0.85rem; margin: 0 0 1.25rem; }
    .fsl-ring  {
        width: 40px; height: 40px;
        border: 3px solid rgba(99,102,241,0.18);
        border-top-color: #818cf8; border-radius: 50%;
        animation: fsl-spin 0.85s linear infinite;
    }
    @keyframes fsl-spin  { to { transform: rotate(360deg); } }
    @keyframes fsl-pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    </style>
    <div id="fs-loader">
        <div class="fsl-icon">💡</div>
        <p class="fsl-title">FinSight</p>
        <p class="fsl-sub">Loading your workspace…</p>
        <div class="fsl-ring"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

from components.auth import logout, restore_session_from_cookies  # noqa: E402
from frontend import budgeting, chat_ai, dashboard, landing                        # noqa: E402
from backend.supabase_client import exchange_code_for_session, update_user_password  # noqa: E402

_loader.empty()


# ─── Session init ─────────────────────────────────────────────────────────────

def _init_session() -> None:
    for key, val in {
        "logged_in":    False,
        "user_id":      None,
        "user_email":   None,
        "access_token": None,
        "show_auth":    False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─── Password reset callback ──────────────────────────────────────────────────

@st.dialog("Set New Password", width="small")
def _password_reset_dialog(code: str) -> None:
    st.markdown(
        """
        <style>
        [data-testid="stDialog"] h2 { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="text-align:center;padding:0.5rem 0 1.25rem">
            <span style="font-size:2rem;filter:drop-shadow(0 0 16px rgba(99,102,241,0.6))">🔑</span>
            <div style="font-size:1.3rem;font-weight:800;
                        color:#e2e8f0;margin:0.4rem 0 0.15rem;letter-spacing:-0.3px">
                Set New Password
            </div>
            <div style="font-size:0.8rem;color:#475569">
                Choose a strong password for your FinSight account
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Exchange the recovery code for a live session first
    if not st.session_state.get("_recovery_session_set"):
        with st.spinner("Verifying reset link…"):
            result = exchange_code_for_session(code)
        if result["error"]:
            st.error(f"Reset link is invalid or expired — {result['error']}")
            if st.button("Request a new link"):
                st.query_params.clear()
                st.rerun()
            return
        # Persist the recovery session so we can call update_user
        session = result["session"]
        if session:
            st.session_state.access_token = session.access_token
        st.session_state._recovery_session_set = True

    with st.form("new_password_form"):
        pw      = st.text_input("New Password",     placeholder="Min. 6 characters", type="password")
        confirm = st.text_input("Confirm Password", placeholder="Repeat password",   type="password")
        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Update Password →", use_container_width=True)

    if submitted:
        if not pw or not confirm:
            st.error("Both fields are required.")
        elif pw != confirm:
            st.error("Passwords do not match.")
        elif len(pw) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            with st.spinner("Updating password…"):
                res = update_user_password(pw)
            if res["error"]:
                st.error(f"Could not update password — {res['error']}")
            else:
                st.success("✅ Password updated! You can now log in.")
                st.session_state._recovery_session_set = False
                st.query_params.clear()


def _handle_recovery_params() -> bool:
    """Check URL for Supabase recovery code. Returns True if recovery flow is active."""
    params = st.query_params
    code = params.get("code")
    if code:
        _password_reset_dialog(code)
        return True
    return False


# ─── Sidebar ──────────────────────────────────────────────────────────────────

# AI Insights first — the highlight feature of FinSight
PAGES = {
    "🧠  AI Insights": chat_ai,
    "📊  Dashboard":   dashboard,
    "💰  Budgeting":   budgeting,
}


def _render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.5rem 0.5rem 1rem;text-align:center">
                <div style="display:flex;flex-direction:column;align-items:center;gap:6px;margin-bottom:4px">
                    <span style="font-size:2rem">💡</span>
                    <div>
                        <div style="font-size:1.3rem;font-weight:800;color:#f1f5f9;
                                    letter-spacing:-0.3px">FinSight</div>
                        <div style="font-size:0.75rem;color:#475569;font-weight:600;
                                    text-transform:uppercase;letter-spacing:0.07em">
                            AI Finance Tracker
                        </div>
                    </div>
                </div>
                <div style="font-size:0.78rem;color:#475569;margin-top:6px;
                            word-break:break-all">
                    {email}
                </div>
            </div>
            """.format(email=st.session_state.user_email or ""),
            unsafe_allow_html=True,
        )
        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.05);margin:0 0 0.75rem 0'>",
            unsafe_allow_html=True,
        )
        selected = st.radio("nav", list(PAGES.keys()), label_visibility="collapsed")
        st.markdown("<div style='min-height:200px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.05);margin:0 0 0.75rem 0'>",
            unsafe_allow_html=True,
        )
        if st.button("  Log Out", use_container_width=True):
            logout()
    return selected  # type: ignore[return-value]


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    _init_session()

    # Handle Supabase password-reset callback (?code=... in URL)
    if _handle_recovery_params():
        landing.render()
        return

    if not st.session_state.logged_in:
        restore_session_from_cookies()

    if not st.session_state.logged_in:
        landing.render()  # dialog is triggered from within landing
        return

    # Clear auth flags on successful login
    st.session_state.show_auth = False
    st.session_state.auth_mode = None

    page = _render_sidebar()
    PAGES[page].render()


if __name__ == "__main__":
    main()
