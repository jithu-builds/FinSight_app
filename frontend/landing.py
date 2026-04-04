"""
FinSight landing page — shown to unauthenticated users before the auth form.
"""

import streamlit as st

LANDING_CSS = """
<style>
/* ── Hide sidebar on landing page ── */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── Full-width layout ── */
.block-container {
    max-width: 100% !important;
    padding: 0 3rem !important;
    margin: 0 !important;
}

/* ── Global reset for landing ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Badge ── */
.lp-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.35);
    color: #818cf8; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 6px 16px; border-radius: 99px;
}

/* ── Hero ── */
.lp-hero {
    text-align: center;
    padding: 4rem 1rem 2.5rem;
}
.lp-hero h1 {
    font-size: clamp(2.4rem, 5vw, 3.8rem) !important;
    font-weight: 800 !important;
    color: #f1f5f9 !important;
    line-height: 1.1 !important;
    letter-spacing: -1.5px !important;
    margin: 1rem 0 1.25rem !important;
}
.lp-hero .gt {
    background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.lp-hero p {
    color: #94a3b8; font-size: 1.05rem; line-height: 1.75;
    max-width: 540px; margin: 0 auto 0.5rem;
}

/* ── Stats bar ── */
.lp-stats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    border-top: 1px solid rgba(255,255,255,0.07);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.015);
    margin: 1.5rem 0;
}
.lp-stat {
    text-align: center; padding: 2rem 1rem;
    border-right: 1px solid rgba(255,255,255,0.07);
}
.lp-stat:last-child { border-right: none; }
.lp-stat .sv {
    font-size: 1.65rem; font-weight: 800; color: #f1f5f9;
    letter-spacing: -0.5px;
}
.lp-stat .sl {
    font-size: 0.7rem; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin-top: 5px;
}

/* ── Section labels ── */
.lp-sec-tag {
    text-align: center; font-size: 0.72rem; font-weight: 700;
    color: #6366f1; letter-spacing: 0.18em; text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.lp-sec-title {
    text-align: center; font-size: 1.9rem; font-weight: 800;
    color: #f1f5f9; letter-spacing: -0.5px; margin-bottom: 0.4rem;
}
.lp-sec-sub {
    text-align: center; color: #64748b; font-size: 0.92rem;
    max-width: 520px; margin: 0 auto 2.5rem;
}

/* ── Feature cards ── */
.lp-feat {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 1.75rem 1.5rem;
    height: 100%; transition: border-color 0.25s, transform 0.25s;
    margin-bottom: 0.5rem;
}
.lp-feat:hover {
    border-color: rgba(99,102,241,0.35);
    transform: translateY(-3px);
}
.lp-feat-icon { font-size: 2.2rem; margin-bottom: 0.9rem; line-height: 1; }
.lp-feat-title {
    font-size: 1.05rem; font-weight: 700; color: #f1f5f9;
    margin-bottom: 0.5rem;
}
.lp-feat-desc { font-size: 0.875rem; color: #64748b; line-height: 1.65; }

/* ── Steps ── */
.lp-step { text-align: center; padding: 0.5rem 1rem 1.5rem; }
.lp-step-num {
    width: 54px; height: 54px; border-radius: 50%;
    background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; font-weight: 800; color: #fff;
    margin: 0 auto 1rem;
    box-shadow: 0 8px 28px rgba(99,102,241,0.45);
}
.lp-step-title {
    font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.45rem;
}
.lp-step-desc { font-size: 0.875rem; color: #64748b; line-height: 1.65; }

/* ── Bottom CTA banner ── */
.lp-cta-banner {
    text-align: center;
    background: linear-gradient(135deg,
        rgba(99,102,241,0.1) 0%,
        rgba(20,184,166,0.07) 100%);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 24px;
    padding: 3.5rem 1.5rem 1.5rem;
    margin: 2rem 0 1rem;
}
.lp-cta-banner h2 {
    font-size: 1.8rem !important; font-weight: 800 !important;
    color: #f1f5f9 !important; margin-bottom: 0.5rem !important;
}
.lp-cta-banner p { color: #64748b; margin-bottom: 0; }

/* ── Trust bar ── */
.lp-trust {
    display: flex; justify-content: center; align-items: center;
    gap: 2.5rem; padding: 1.5rem 0 2rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    flex-wrap: wrap;
}
.lp-trust-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.8rem; color: #475569; font-weight: 500;
}

/* ── Button overrides for landing CTAs ── */
.lp-btn-wrap .stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%) !important;
    font-size: 1rem !important; padding: 0.7rem 1.5rem !important;
    border-radius: 12px !important; font-weight: 700 !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.45) !important;
    letter-spacing: 0.01em !important;
}
.lp-btn-wrap .stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-2px) !important;
    box-shadow: 0 12px 36px rgba(99,102,241,0.55) !important;
}

/* Nav sign-in button — subtle outline style */
.lp-nav-btn .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e2e8f0 !important; font-size: 0.9rem !important;
    padding: 0.45rem 1.1rem !important; border-radius: 10px !important;
    box-shadow: none !important; font-weight: 600 !important;
}
.lp-nav-btn .stButton > button:hover {
    background: rgba(99,102,241,0.18) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #c7d2fe !important; transform: none !important;
}
</style>
"""


def render() -> None:
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    # ── Navbar ─────────────────────────────────────────────────────────────────
    # Thin top bar: just Sign In button pinned to the right
    _, nav_right = st.columns([5, 1])
    with nav_right:
        st.markdown("<div style='padding:0.6rem 0'>", unsafe_allow_html=True)
        st.markdown("<div class='lp-nav-btn'>", unsafe_allow_html=True)
        if st.button("Sign In →", key="nav_signin", use_container_width=True):
            st.session_state.show_auth = True
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Centred hero brand — large and prominent
    st.markdown(
        """
        <div style="text-align:center;padding:2.5rem 0 0.5rem;
                    display:flex;flex-direction:column;align-items:center;gap:0.4rem">
            <div style="font-size:5rem;line-height:1;filter:drop-shadow(0 0 28px rgba(99,102,241,0.6))">
                💡
            </div>
            <div style="font-size:3.5rem;font-weight:900;color:#f1f5f9;
                        letter-spacing:-1.5px;line-height:1">
                FinSight
            </div>
            <div style="font-size:0.8rem;font-weight:700;color:#334155;
                        text-transform:uppercase;letter-spacing:0.2em">
                AI Finance Tracker
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="lp-hero">
            <div class="lp-badge">✦ AI-POWERED PERSONAL FINANCE</div>
            <h1>
                Stop guessing<br>
                where your money <span class="gt">actually goes</span>
            </h1>
            <p>
                Upload your bank statement once. Our AI reads every transaction,
                categorises your spending, and tells you exactly where to cut back.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hero CTA button
    _, cta_col, _ = st.columns([1.5, 1, 1.5])
    with cta_col:
        st.markdown("<div class='lp-btn-wrap'>", unsafe_allow_html=True)
        if st.button("🚀  Get Started — Free", key="hero_cta", use_container_width=True):
            st.session_state.show_auth = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Stats bar ──────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="lp-stats">
            <div class="lp-stat">
                <div class="sv">PDF → Data</div>
                <div class="sl">In Seconds</div>
            </div>
            <div class="lp-stat">
                <div class="sv">FinSight AI</div>
                <div class="sl">AI Engine</div>
            </div>
            <div class="lp-stat">
                <div class="sv">100%</div>
                <div class="sl">Data Isolated</div>
            </div>
            <div class="lp-stat">
                <div class="sv">Zero</div>
                <div class="sl">Manual Entry Needed</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Features ───────────────────────────────────────────────────────────────
    st.markdown("<div style='padding:2.5rem 0 0'>", unsafe_allow_html=True)
    st.markdown('<div class="lp-sec-tag">FEATURES</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lp-sec-title">Everything you need to understand your finances</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="lp-sec-sub">No spreadsheets. No manual categorising. Just upload and get answers.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2, gap="medium")
    with f1:
        st.markdown(
            """
            <div class="lp-feat">
                <div class="lp-feat-icon">📄</div>
                <div class="lp-feat-title">Smart PDF Import</div>
                <div class="lp-feat-desc">
                    Drop in any bank statement PDF. We extract every transaction automatically —
                    no templates, no manual mapping, any bank format worldwide.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="lp-feat">
                <div class="lp-feat-icon">🧠</div>
                <div class="lp-feat-title">AI Categorisation</div>
                <div class="lp-feat-desc">
                    FinSight AI reads your transactions and assigns categories like Food, Transport,
                    and Shopping — with context and reasoning, not just keywords.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    f3, f4 = st.columns(2, gap="medium")
    with f3:
        st.markdown(
            """
            <div class="lp-feat">
                <div class="lp-feat-icon">📊</div>
                <div class="lp-feat-title">Visual Dashboard</div>
                <div class="lp-feat-desc">
                    Pie charts, bar charts, and monthly trend graphs so you can see at a glance
                    where your money is going — without opening a spreadsheet.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f4:
        st.markdown(
            """
            <div class="lp-feat">
                <div class="lp-feat-icon">💡</div>
                <div class="lp-feat-title">Insights & Predictions</div>
                <div class="lp-feat-desc">
                    Get a spending health score, end-of-month predictions, and specific tips like
                    "You visited Starbucks 9 times — that's $38 you could save."
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── How it works ───────────────────────────────────────────────────────────
    st.markdown("<div style='padding:3rem 0 0'>", unsafe_allow_html=True)
    st.markdown('<div class="lp-sec-tag">HOW IT WORKS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lp-sec-title">From PDF to insights in three steps</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="lp-sec-sub">No setup, no linking bank accounts, no waiting.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        st.markdown(
            """
            <div class="lp-step">
                <div class="lp-step-num">1</div>
                <div class="lp-step-title">Upload your statement</div>
                <div class="lp-step-desc">
                    Export a PDF from your bank's website and drop it into the Dashboard.
                    Any bank, any format.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            """
            <div class="lp-step">
                <div class="lp-step-num">2</div>
                <div class="lp-step-title">AI does the work</div>
                <div class="lp-step-desc">
                    FinSight AI reads every line, extracts transactions, and assigns
                    categories in seconds — not hours.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            """
            <div class="lp-step">
                <div class="lp-step-num">3</div>
                <div class="lp-step-title">Take action</div>
                <div class="lp-step-desc">
                    Review your spending score, set AI-suggested budgets, and get specific
                    recommendations for the month ahead.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Trust bar ──────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="lp-trust">
            <div class="lp-trust-item">🔒&nbsp; Supabase Auth — encrypted &amp; secure</div>
            <div class="lp-trust-item">🛡️&nbsp; Row-level security — your data is yours only</div>
            <div class="lp-trust-item">🚫&nbsp; We never store your PDF</div>
            <div class="lp-trust-item">👤&nbsp; No data sharing, ever</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
