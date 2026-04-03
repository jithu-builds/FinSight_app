"""
AI Personal Finance Tracker — Streamlit entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st
import extra_streamlit_components as stx
from components.session_store import set_cm

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Create CookieManager ONCE per render and register it in the shared store.
# auth.py reads it via session_store.get_cm() — no circular imports, no duplicates.
set_cm(stx.CookieManager(key="finance_tracker_cookies"))

# ─── Global CSS ───────────────────────────────────────────────────────────────
# Injected before any imports so the dark background is visible immediately.

GLOBAL_CSS = """
<style>
.stApp {
    background: #0f172a;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

[data-testid="stSidebar"] {
    background: #0c1222 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
[data-testid="stSidebar"] .stRadio label {
    display: flex; align-items: center;
    padding: 0.6rem 0.9rem; border-radius: 10px;
    color: #94a3b8 !important; font-weight: 500; font-size: 0.9rem;
    cursor: pointer; transition: background 0.15s, color 0.15s; margin-bottom: 2px;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(129,140,248,0.1); color: #c7d2fe !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(99,102,241,0.18) !important; color: #818cf8 !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { margin: 0; }
[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none; }

.block-container { padding: 1.75rem 2.5rem 2rem !important; max-width: 1400px; }

h1 { font-size:1.75rem !important; font-weight:700 !important; color:#f1f5f9 !important; letter-spacing:-0.4px !important; margin-bottom:0.25rem !important; }
h2 { font-size:1.2rem !important; font-weight:600 !important; color:#e2e8f0 !important; }
h3 { font-size:1rem !important; font-weight:600 !important; color:#cbd5e1 !important; }

[data-testid="stMetric"] {
    background: #1e293b; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.1rem 1.3rem !important; transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover { border-color: rgba(99,102,241,0.3); }
[data-testid="stMetricLabel"] { color:#64748b !important; font-size:0.78rem !important; font-weight:600 !important; text-transform:uppercase !important; letter-spacing:0.07em !important; }
[data-testid="stMetricValue"] { color:#f1f5f9 !important; font-size:1.6rem !important; font-weight:700 !important; }
[data-testid="stMetricDelta"] svg { display: none; }

.stButton button, .stFormSubmitButton button {
    background: linear-gradient(135deg, #6366f1, #818cf8) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.875rem !important; padding: 0.55rem 1.25rem !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.35) !important;
    transition: opacity 0.2s, transform 0.1s, box-shadow 0.2s !important;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    opacity: 0.88 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(99,102,241,0.45) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: rgba(239,68,68,0.12) !important; color: #f87171 !important;
    box-shadow: none !important; border: 1px solid rgba(239,68,68,0.2) !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(239,68,68,0.22) !important; transform: none !important; box-shadow: none !important;
}

.stTextInput label, .stNumberInput label, .stSelectbox label {
    color: #64748b !important; font-size: 0.78rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important;
}
.stTextInput input, .stNumberInput input {
    background: #1e293b !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}

[data-testid="stFileUploader"] {
    background: #1e293b !important; border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 14px !important; padding: 1rem !important; transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(99,102,241,0.6) !important; }

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important; overflow: hidden !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #1e293b !important; border-radius: 12px !important;
    padding: 4px !important; gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; color: #64748b !important;
    font-weight: 500 !important; padding: 0.45rem 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#6366f1,#818cf8) !important;
    color: #fff !important; box-shadow: 0 3px 10px rgba(99,102,241,0.35) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

[data-testid="stExpander"] {
    background: #1e293b !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.25rem 0 !important; }

[data-testid="stChatMessage"] {
    background: #1e293b !important; border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important; padding: 0.9rem 1.1rem !important; margin-bottom: 0.6rem !important;
}
[data-testid="stChatInputTextArea"] {
    background: #1e293b !important; border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important; color: #f1f5f9 !important;
}

.stAlert { border-radius: 10px !important; border: none !important; font-size: 0.875rem !important; }

/* ── Spinner — accent colour only, no layout override ───────────── */
.stSpinner [data-testid="stSpinner"] div,
div[data-testid="stSpinner"] > div > div {
    border-top-color: #818cf8 !important;
}
</style>
"""

# ── Inject CSS immediately so the dark background is visible right away ───────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Load all heavy modules INSIDE a spinner so the user sees feedback ─────────
# This is the key fix: Streamlit sends the spinner to the browser first,
# then runs the imports. Without this, a blank screen shows for several seconds.
with st.spinner("Loading Finance Tracker…"):
    from components.auth import logout, restore_session_from_cookies, show_auth_page  # noqa: E402
    from frontend import budgeting, chat_ai, dashboard                                # noqa: E402


# ─── Session init ─────────────────────────────────────────────────────────────

def _init_session() -> None:
    for key, val in {
        "logged_in":    False,
        "user_id":      None,
        "user_email":   None,
        "access_token": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─── Sidebar ──────────────────────────────────────────────────────────────────

PAGES = {
    "📊  Dashboard":  dashboard,
    "💰  Budgeting":  budgeting,
    "🧠  AI Insights": chat_ai,
}


def _render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.5rem 0.25rem 1rem">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                    <span style="font-size:1.6rem">💰</span>
                    <span style="font-size:1.15rem;font-weight:700;color:#f1f5f9">
                        Finance Tracker
                    </span>
                </div>
                <div style="font-size:0.75rem;color:#475569;padding-left:2px">{email}</div>
            </div>
            """.format(email=st.session_state.user_email),
            unsafe_allow_html=True,
        )
        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.06);margin:0 0 1rem 0'>",
            unsafe_allow_html=True,
        )
        selected = st.radio("nav", list(PAGES.keys()), label_visibility="collapsed")
        st.markdown("<div style='min-height:200px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.06);margin:0 0 0.75rem 0'>",
            unsafe_allow_html=True,
        )
        if st.button("  Log Out", use_container_width=True):
            logout()
    return selected  # type: ignore[return-value]


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    _init_session()

    # Try to restore session from cookies before showing auth page.
    # This is what keeps the user logged in across browser refreshes.
    if not st.session_state.logged_in:
        restore_session_from_cookies()

    if not st.session_state.logged_in:
        show_auth_page()
        return

    page = _render_sidebar()
    PAGES[page].render()


if __name__ == "__main__":
    main()
