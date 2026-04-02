"""
AI Personal Finance Tracker — Streamlit entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st

# ── Page config must be the first Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="AI Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.auth import logout, show_auth_page  # noqa: E402 (after set_page_config)
from frontend import budgeting, chat_ai, dashboard   # noqa: E402


# ─── Session state initialisation ────────────────────────────────────────────

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


# ─── Sidebar (shown only when logged in) ──────────────────────────────────────

PAGES = {
    "📊 Dashboard":    dashboard,
    "💰 Budgeting":    budgeting,
    "🤖 AI Advisor":   chat_ai,
}


def _render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            f"""
            <div style='padding:12px 0 8px 0'>
                <h3 style='margin:0'>💰 Finance Tracker</h3>
                <p style='color:grey; font-size:0.82em; margin:4px 0 0 0'>
                    {st.session_state.user_email}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        selected = st.radio(
            "Navigate",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.divider()

        if st.button("🚪 Log Out", use_container_width=True):
            logout()

    return selected  # type: ignore[return-value]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    _init_session()

    if not st.session_state.logged_in:
        show_auth_page()
        return

    selected_page = _render_sidebar()
    PAGES[selected_page].render()


if __name__ == "__main__":
    main()
