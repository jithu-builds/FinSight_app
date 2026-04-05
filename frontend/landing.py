"""
FinSight landing page — Mint-inspired design, shown to unauthenticated users.
"""

import streamlit as st

LANDING_CSS = """
<style>
/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

/* ── Override app background on landing page ── */
.stApp { background: #1a1512 !important; }

[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }

.block-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ── Nav ── */
.lp-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 3rem;
    height: 68px;
    background: rgba(26,21,18,0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(244,236,220,0.07);
    position: sticky; top: 0; z-index: 100;
}
.lp-nav-logo {
    display: flex; align-items: center; gap: 14px;
    text-decoration: none;
}
.lp-nav-logo-icon {
    width: 46px; height: 46px; border-radius: 50%;
    background: #1a1a1a;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.lp-nav-logo-text { display: flex; flex-direction: column; gap: 1px; }
.lp-nav-logo-name {
    font-size: 1.3rem; font-weight: 800; color: #1a1a1a;
    letter-spacing: -0.3px; line-height: 1;
}
.lp-nav-logo-sub {
    font-size: 0.58rem; font-weight: 600; color: #9a9a9a;
    letter-spacing: 0.18em; text-transform: uppercase; line-height: 1;
}
.lp-nav-links {
    display: flex; align-items: center; gap: 2rem;
    list-style: none;
}
.lp-nav-links a {
    color: #7a6b60; font-size: 0.875rem; font-weight: 600;
    text-decoration: none; transition: color 0.2s;
    letter-spacing: 0.01em;
}
.lp-nav-links a:hover { color: #000; }
.lp-nav-actions { display: flex; align-items: center; gap: 0.75rem; }
.lp-nav-btn-ghost, .lp-nav-btn-cta {
    display: inline-flex; align-items: center;
    background: #6c73f0;
    border: none;
    cursor: pointer;
    color: #ffffff !important; font-size: 0.875rem; font-weight: 600;
    padding: 0.5rem 1.3rem; border-radius: 10px;
    text-decoration: none !important;
    transition: background 0.2s, opacity 0.2s;
    box-shadow: 0 4px 14px rgba(108,115,240,0.35);
}
.lp-nav-btn-ghost:hover, .lp-nav-btn-cta:hover {
    background: #5a61e0;
    color: #ffffff !important;
    text-decoration: none !important;
    opacity: 0.92;
}

/* ── Hero ── */
.lp-hero-wrap {
    display: grid; grid-template-columns: 1fr 1fr;
    align-items: center; gap: 3rem;
    padding: 5rem 3rem 4rem;
    max-width: 1300px; margin: 0 auto;
    min-height: 580px;
}
.lp-hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(189,134,106,0.12);
    border: 1px solid rgba(189,134,106,0.3);
    color: #d4a080; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 99px;
    margin-bottom: 1.25rem;
}
.lp-hero-h1 {
    font-size: clamp(2.4rem, 4vw, 3.6rem) !important;
    font-weight: 900 !important; color: #F4ECDC !important;
    line-height: 1.08 !important; letter-spacing: -1.5px !important;
    margin-bottom: 1.25rem !important;
}
.lp-hero-h1 .grad {
    background: linear-gradient(135deg, #BD866A 0%, #BD866A 60%, #d4a080 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.lp-hero-sub {
    color: #b8a898; font-size: 1.05rem; line-height: 1.75;
    max-width: 480px; margin-bottom: 2rem;
}
.lp-hero-actions {
    display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
    margin-bottom: 2.5rem;
}
.lp-hero-social {
    display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
}
.lp-hero-social-item {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.78rem; color: #5c4e46; font-weight: 500;
}

/* ── Dashboard mockup ── */
.lp-mockup {
    background: #221c18;
    border: 1px solid rgba(244,236,220,0.09);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(244,236,220,0.05);
    position: relative;
    overflow: hidden;
}
.lp-mockup::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(189,134,106,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.lp-mock-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.25rem;
}
.lp-mock-title { font-size: 0.8rem; font-weight: 700; color: #7a6b60; text-transform: uppercase; letter-spacing: 0.1em; }
.lp-mock-badge { background: rgba(189,134,106,0.15); color: #d4a080; font-size: 0.65rem; font-weight: 700; padding: 3px 10px; border-radius: 99px; letter-spacing: 0.08em; }
.lp-mock-balance { font-size: 2rem; font-weight: 900; color: #F4ECDC; letter-spacing: -1px; margin-bottom: 0.25rem; }
.lp-mock-balance-label { font-size: 0.72rem; color: #5c4e46; font-weight: 600; margin-bottom: 1.25rem; }
.lp-mock-cats {
    display: flex; flex-direction: column; gap: 0.6rem;
    margin-bottom: 1.25rem;
}
.lp-mock-cat { display: flex; flex-direction: column; gap: 5px; }
.lp-mock-cat-row { display: flex; justify-content: space-between; align-items: center; }
.lp-mock-cat-label { font-size: 0.72rem; font-weight: 600; color: #b8a898; }
.lp-mock-cat-amount { font-size: 0.72rem; font-weight: 700; color: #F4ECDC; }
.lp-mock-bar-bg { height: 5px; background: rgba(244,236,220,0.07); border-radius: 99px; overflow: hidden; }
.lp-mock-bar-fill { height: 100%; border-radius: 99px; }
.lp-mock-divider { border: none; border-top: 1px solid rgba(244,236,220,0.06); margin: 1rem 0; }
.lp-mock-txns { display: flex; flex-direction: column; gap: 0.55rem; }
.lp-mock-txn { display: flex; align-items: center; justify-content: space-between; }
.lp-mock-txn-left { display: flex; align-items: center; gap: 10px; }
.lp-mock-txn-icon {
    width: 30px; height: 30px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
}
.lp-mock-txn-name { font-size: 0.75rem; font-weight: 600; color: #ede0cc; }
.lp-mock-txn-date { font-size: 0.65rem; color: #5c4e46; }
.lp-mock-txn-amt { font-size: 0.78rem; font-weight: 700; }
.lp-mock-txn-amt.neg { color: #c97b6e; }
.lp-mock-txn-amt.pos { color: #d4a080; }

/* ── Trusted strip ── */
.lp-trusted {
    background: rgba(244,236,220,0.03);
    border-top: 1px solid rgba(244,236,220,0.06);
    border-bottom: 1px solid rgba(244,236,220,0.06);
    padding: 1.25rem 3rem;
    display: flex; align-items: center; justify-content: center; gap: 3rem;
    flex-wrap: wrap;
}
.lp-trusted-label { font-size: 0.7rem; font-weight: 700; color: #4a403a; letter-spacing: 0.12em; text-transform: uppercase; }
.lp-trusted-item { font-size: 0.8rem; font-weight: 600; color: #4a403a; letter-spacing: 0.02em; }

/* ── Stats bar ── */
.lp-stats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    max-width: 900px; margin: 3.5rem auto;
    border: 1px solid rgba(244,236,220,0.08);
    border-radius: 20px; overflow: hidden;
    background: rgba(255,255,255,0.02);
}
.lp-stat {
    text-align: center; padding: 2rem 1rem;
    border-right: 1px solid rgba(244,236,220,0.08);
}
.lp-stat:last-child { border-right: none; }
.lp-stat-val { font-size: 1.8rem; font-weight: 900; color: #F4ECDC; letter-spacing: -0.5px; }
.lp-stat-val .accent { color: #BD866A; }
.lp-stat-lbl { font-size: 0.68rem; font-weight: 700; color: #5c4e46; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 5px; }

/* ── Section header ── */
.lp-sec-wrap { text-align: center; margin-bottom: 3rem; padding: 0 1rem; }
.lp-sec-tag { font-size: 0.7rem; font-weight: 700; color: #BD866A; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 0.6rem; }
.lp-sec-h2 { font-size: clamp(1.6rem, 3vw, 2.2rem); font-weight: 900; color: #F4ECDC; letter-spacing: -0.5px; margin-bottom: 0.75rem; }
.lp-sec-sub { font-size: 0.95rem; color: #7a6b60; max-width: 520px; margin: 0 auto; line-height: 1.7; }

/* ── Feature rows (alternating) ── */
.lp-feat-row {
    display: grid; grid-template-columns: 1fr 1fr;
    align-items: center; gap: 4rem;
    max-width: 1200px; margin: 0 auto 5rem;
    padding: 0 3rem;
}
.lp-feat-row.reverse { direction: rtl; }
.lp-feat-row.reverse > * { direction: ltr; }
.lp-feat-tag { font-size: 0.68rem; font-weight: 700; color: #BD866A; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 0.75rem; }
.lp-feat-h3 { font-size: 1.75rem; font-weight: 900; color: #F4ECDC; letter-spacing: -0.5px; margin-bottom: 1rem; line-height: 1.2; }
.lp-feat-p { font-size: 0.92rem; color: #7a6b60; line-height: 1.75; margin-bottom: 1.5rem; }
.lp-feat-bullets { list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }
.lp-feat-bullets li { display: flex; align-items: flex-start; gap: 10px; font-size: 0.875rem; color: #b8a898; line-height: 1.5; }
.lp-feat-bullets li::before { content: '✓'; color: #BD866A; font-weight: 700; flex-shrink: 0; margin-top: 1px; }

/* ── Feature panels ── */
.lp-panel {
    background: #221c18;
    border: 1px solid rgba(244,236,220,0.08);
    border-radius: 20px; padding: 1.75rem;
    box-shadow: 0 24px 60px rgba(0,0,0,0.4);
}
.lp-panel-header { font-size: 0.72rem; font-weight: 700; color: #5c4e46; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1.25rem; }
.lp-budget-item { margin-bottom: 1rem; }
.lp-budget-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.lp-budget-name { font-size: 0.8rem; font-weight: 600; color: #ede0cc; }
.lp-budget-pct { font-size: 0.75rem; font-weight: 700; }
.lp-budget-bg { height: 8px; background: rgba(244,236,220,0.07); border-radius: 99px; overflow: hidden; }
.lp-budget-fill { height: 100%; border-radius: 99px; }
.lp-insight-card {
    background: rgba(244,236,220,0.05);
    border: 1px solid rgba(244,236,220,0.07);
    border-radius: 14px; padding: 1rem 1.25rem;
    margin-bottom: 0.75rem; display: flex; align-items: flex-start; gap: 12px;
}
.lp-insight-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
.lp-insight-text { font-size: 0.82rem; color: #b8a898; line-height: 1.55; }
.lp-insight-text strong { color: #F4ECDC; display: block; margin-bottom: 3px; font-size: 0.85rem; }
.lp-score-ring {
    width: 100px; height: 100px; border-radius: 50%;
    border: 8px solid #BD866A;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    margin: 0 auto 1rem;
    box-shadow: 0 0 24px rgba(189,134,106,0.3);
}
.lp-score-num { font-size: 1.6rem; font-weight: 900; color: #F4ECDC; line-height: 1; }
.lp-score-lbl { font-size: 0.55rem; font-weight: 700; color: #BD866A; text-transform: uppercase; letter-spacing: 0.1em; }
.lp-score-row { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.lp-score-item { text-align: center; }
.lp-score-item-val { font-size: 0.95rem; font-weight: 800; color: #F4ECDC; }
.lp-score-item-lbl { font-size: 0.62rem; color: #5c4e46; font-weight: 600; }

/* ── How it works ── */
.lp-steps {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem; max-width: 900px; margin: 0 auto;
    padding: 0 3rem;
}
.lp-step { text-align: center; padding: 2rem 1.5rem; }
.lp-step-num {
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg, #BD866A 0%, #BD866A 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 900; color: #fff;
    margin: 0 auto 1.25rem;
    box-shadow: 0 8px 28px rgba(189,134,106,0.4);
}
.lp-step-title { font-size: 1rem; font-weight: 700; color: #F4ECDC; margin-bottom: 0.6rem; }
.lp-step-desc { font-size: 0.85rem; color: #7a6b60; line-height: 1.65; }
.lp-step-connector {
    display: flex; align-items: center; justify-content: center;
    padding-top: 1rem; color: #3a2f28; font-size: 1.5rem;
}

/* ── Testimonials ── */
.lp-testimonials {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem; max-width: 1100px; margin: 0 auto;
    padding: 0 3rem;
}
.lp-tcard {
    background: rgba(244,236,220,0.04);
    border: 1px solid rgba(244,236,220,0.08);
    border-radius: 20px; padding: 1.75rem;
    transition: border-color 0.25s, transform 0.25s;
}
.lp-tcard:hover { border-color: rgba(189,134,106,0.3); transform: translateY(-3px); }
.lp-tcard-stars { color: #BD866A; font-size: 0.85rem; margin-bottom: 1rem; letter-spacing: 2px; }
.lp-tcard-quote { font-size: 0.875rem; color: #b8a898; line-height: 1.7; margin-bottom: 1.5rem; font-style: italic; }
.lp-tcard-author { display: flex; align-items: center; gap: 10px; }
.lp-tcard-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; color: #fff;
    flex-shrink: 0;
}
.lp-tcard-name { font-size: 0.82rem; font-weight: 700; color: #ede0cc; }
.lp-tcard-role { font-size: 0.72rem; color: #5c4e46; }

/* ── Security section ── */
.lp-security {
    background: rgba(189,134,106,0.04);
    border-top: 1px solid rgba(189,134,106,0.1);
    border-bottom: 1px solid rgba(189,134,106,0.1);
    padding: 3rem;
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 2rem; max-width: 1100px; margin: 0 auto;
}
.lp-sec-item { text-align: center; }
.lp-sec-icon { font-size: 1.75rem; margin-bottom: 0.75rem; }
.lp-sec-title-sm { font-size: 0.875rem; font-weight: 700; color: #ede0cc; margin-bottom: 0.35rem; }
.lp-sec-desc { font-size: 0.78rem; color: #7a6b60; line-height: 1.55; }

/* ── CTA banner ── */
.lp-cta-banner {
    text-align: center;
    background: linear-gradient(135deg, rgba(189,134,106,0.08) 0%, rgba(137,104,95,0.08) 100%);
    border: 1px solid rgba(189,134,106,0.15);
    border-radius: 24px;
    padding: 4rem 2rem 2.5rem;
    margin: 4rem 3rem 1rem;
}
.lp-cta-h2 { font-size: 2rem; font-weight: 900; color: #F4ECDC; letter-spacing: -0.5px; margin-bottom: 0.6rem; }
.lp-cta-sub { font-size: 0.95rem; color: #7a6b60; margin-bottom: 0; }

/* ── Footer ── */
.lp-footer {
    border-top: 1px solid rgba(244,236,220,0.06);
    padding: 2.5rem 3rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 1rem;
    margin-top: 2rem;
}
.lp-footer-logo { font-size: 1.1rem; font-weight: 900; color: #4a403a; letter-spacing: -0.3px; }
.lp-footer-links { display: flex; gap: 2rem; }
.lp-footer-links a { font-size: 0.78rem; color: #4a403a; text-decoration: none; font-weight: 500; }
.lp-footer-links a:hover { color: #7a6b60; }
.lp-footer-copy { font-size: 0.72rem; color: #3a2f28; font-weight: 500; }

/* ── Button overrides ── */
.lp-btn-primary .stButton > button {
    background: linear-gradient(135deg, #BD866A 0%, #89685F 100%) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 0.65rem 1.6rem !important;
    box-shadow: 0 8px 24px rgba(189,134,106,0.4) !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s !important;
}
.lp-btn-primary .stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(189,134,106,0.5) !important;
}
.lp-btn-outline .stButton > button {
    background: rgba(244,236,220,0.06) !important;
    color: #ede0cc !important;
    border: 1px solid rgba(244,236,220,0.13) !important;
    border-radius: 12px !important; font-weight: 600 !important;
    font-size: 0.95rem !important; padding: 0.65rem 1.6rem !important;
    box-shadow: none !important;
}
.lp-btn-outline .stButton > button:hover {
    background: rgba(244,236,220,0.10) !important;
    border-color: rgba(244,236,220,0.24) !important;
    transform: none !important; box-shadow: none !important;
}
.lp-nav-signin .stButton > button {
    background: transparent !important;
    color: #b8a898 !important; border: none !important;
    font-weight: 600 !important; font-size: 0.875rem !important;
    padding: 0.45rem 1rem !important; box-shadow: none !important;
}
.lp-nav-signin .stButton > button:hover {
    color: #F4ECDC !important; transform: none !important;
    box-shadow: none !important;
}
.lp-nav-cta .stButton > button {
    background: linear-gradient(135deg, #BD866A 0%, #89685F 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 0.85rem !important; padding: 0.45rem 1.2rem !important;
    box-shadow: 0 4px 14px rgba(189,134,106,0.35) !important;
}
.lp-cta-btn-wrap .stButton > button {
    background: linear-gradient(135deg, #BD866A 0%, #89685F 100%) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 8px 24px rgba(189,134,106,0.4) !important;
}

/* ── Spacing utils ── */
.lp-section { padding: 4rem 0; }
.lp-section-alt { padding: 4rem 0; background: #F4ECDC; }
.lp-mt-sm { margin-top: 1rem; }
.lp-mt-md { margin-top: 2rem; }
.lp-mt-lg { margin-top: 3rem; }
.lp-center { text-align: center; }

/* ════════════════════════════════════════════════════════════
   LIGHT THEME OVERRIDES  (background: #e9ecef)
   ════════════════════════════════════════════════════════════ */

/* Strip default link styles from nav buttons */
a.lp-nav-btn-ghost, a.lp-nav-btn-cta { text-decoration: none !important; }
a.lp-nav-btn-ghost:hover, a.lp-nav-btn-cta:hover { text-decoration: none !important; }

/* Page & nav */
.stApp { background: #e9ecef !important; }
.lp-nav { background: rgba(233,236,239,0.97) !important; border-bottom-color: rgba(79,73,76,0.12) !important; }
.lp-nav-logo-name { color: #1a1a1a !important; }
.lp-nav-logo-sub { color: #9a9a9a !important; }
.lp-nav-links a { color: #4F494C !important; }
.lp-nav-links a:hover { color: #89685F !important; }

/* Trusted strip */
.lp-trusted { background: #F4ECDC !important; border-color: rgba(79,73,76,0.10) !important; }
.lp-trusted-label, .lp-trusted-item { color: #4F494C !important; }

/* Stats bar */
.lp-stats { background: #ffffff !important; border-color: rgba(79,73,76,0.10) !important; }
.lp-stat { border-right-color: rgba(79,73,76,0.10) !important; }
.lp-stat-val { color: #2d2522 !important; }
.lp-stat-lbl { color: #7a6b60 !important; }

/* Section headings */
.lp-sec-tag { color: #89685F !important; }
.lp-sec-h2 { color: #2d2522 !important; }
.lp-sec-sub { color: #5c4e46 !important; }

/* Hero */
.lp-hero-h1 { color: #2d2522 !important; }
.lp-hero-sub { color: #5c4e46 !important; }
.lp-hero-badge { background: rgba(137,104,95,0.10) !important; border-color: rgba(137,104,95,0.30) !important; color: #89685F !important; }
.lp-hero-social-item { color: #4F494C !important; }

/* Feature text */
.lp-feat-tag { color: #89685F !important; }
.lp-feat-h3 { color: #2d2522 !important; }
.lp-feat-p { color: #5c4e46 !important; }
.lp-feat-bullets li { color: #5c4e46 !important; }
.lp-feat-bullets li::before { color: #BD866A !important; }

/* Steps */
.lp-step-title { color: #2d2522 !important; }
.lp-step-desc { color: #5c4e46 !important; }

/* Testimonials */
.lp-tcard { background: #ffffff !important; border-color: rgba(79,73,76,0.10) !important; }
.lp-tcard:hover { border-color: rgba(189,134,106,0.40) !important; }
.lp-tcard-stars { color: #BD866A !important; }
.lp-tcard-quote { color: #5c4e46 !important; }
.lp-tcard-name { color: #2d2522 !important; }
.lp-tcard-role { color: #7a6b60 !important; }

/* Security */
.lp-security { background: rgba(189,134,106,0.06) !important; border-color: rgba(189,134,106,0.18) !important; }
.lp-sec-title-sm { color: #2d2522 !important; }
.lp-sec-desc { color: #5c4e46 !important; }

/* CTA banner */
.lp-cta-banner { background: linear-gradient(135deg, rgba(189,134,106,0.10) 0%, rgba(137,104,95,0.08) 100%) !important; border-color: rgba(189,134,106,0.25) !important; }
.lp-cta-h2 { color: #2d2522 !important; }
.lp-cta-sub { color: #5c4e46 !important; }

/* Footer */
.lp-footer { border-top-color: rgba(79,73,76,0.12) !important; }
.lp-footer-logo { color: #4F494C !important; }
.lp-footer-links a { color: #4F494C !important; }
.lp-footer-links a:hover { color: #89685F !important; }
.lp-footer-copy { color: #7a6b60 !important; }

/* Nav buttons on light bg */
.lp-nav-signin .stButton > button { color: #4F494C !important; }
.lp-nav-signin .stButton > button:hover { color: #2d2522 !important; }

/* Outline button on light bg */
.lp-btn-outline .stButton > button {
    background: rgba(79,73,76,0.06) !important;
    color: #2d2522 !important;
    border-color: rgba(79,73,76,0.20) !important;
}
.lp-btn-outline .stButton > button:hover {
    background: rgba(79,73,76,0.10) !important;
    border-color: rgba(79,73,76,0.30) !important;
}

/* ── Dark panels stay dark (mockups represent the app UI) ── */
.lp-mockup, .lp-panel { background: #221c18 !important; }
.lp-mock-balance, .lp-mock-cat-amount { color: #F4ECDC !important; }
.lp-mock-cat-label { color: #b8a898 !important; }
.lp-mock-balance-label, .lp-mock-txn-date { color: #5c4e46 !important; }
.lp-mock-txn-name { color: #ede0cc !important; }
.lp-mock-bar-bg, .lp-budget-bg { background: rgba(244,236,220,0.07) !important; }
.lp-budget-name { color: #ede0cc !important; }
.lp-panel-header { color: #7a6b60 !important; }
.lp-insight-text { color: #b8a898 !important; }
.lp-insight-text strong { color: #F4ECDC !important; }
</style>
"""

# ── Dashboard mockup HTML ──────────────────────────────────────────────────────
MOCKUP_HTML = """
<div class="lp-mockup">
    <div class="lp-mock-header">
        <div class="lp-mock-title">My Finances</div>
        <div class="lp-mock-badge">● LIVE</div>
    </div>
    <div class="lp-mock-balance">$3,420</div>
    <div class="lp-mock-balance-label">AVAILABLE BALANCE · OCT 2024</div>
    <div class="lp-mock-cats">
        <div class="lp-mock-cat">
            <div class="lp-mock-cat-row">
                <span class="lp-mock-cat-label">🍔 Food & Dining</span>
                <span class="lp-mock-cat-amount">$680</span>
            </div>
            <div class="lp-mock-bar-bg">
                <div class="lp-mock-bar-fill" style="width:68%;background:linear-gradient(90deg,#BD866A,#89685F)"></div>
            </div>
        </div>
        <div class="lp-mock-cat">
            <div class="lp-mock-cat-row">
                <span class="lp-mock-cat-label">🚗 Transport</span>
                <span class="lp-mock-cat-amount">$240</span>
            </div>
            <div class="lp-mock-bar-bg">
                <div class="lp-mock-bar-fill" style="width:38%;background:linear-gradient(90deg,#BD866A,#d4a080)"></div>
            </div>
        </div>
        <div class="lp-mock-cat">
            <div class="lp-mock-cat-row">
                <span class="lp-mock-cat-label">🛍️ Shopping</span>
                <span class="lp-mock-cat-amount">$450</span>
            </div>
            <div class="lp-mock-bar-bg">
                <div class="lp-mock-bar-fill" style="width:52%;background:linear-gradient(90deg,#c4906e,#89685F)"></div>
            </div>
        </div>
        <div class="lp-mock-cat">
            <div class="lp-mock-cat-row">
                <span class="lp-mock-cat-label">💡 Utilities</span>
                <span class="lp-mock-cat-amount">$150</span>
            </div>
            <div class="lp-mock-bar-bg">
                <div class="lp-mock-bar-fill" style="width:22%;background:linear-gradient(90deg,#BD866A,#89685F)"></div>
            </div>
        </div>
    </div>
    <hr class="lp-mock-divider">
    <div class="lp-mock-txns">
        <div class="lp-mock-txn">
            <div class="lp-mock-txn-left">
                <div class="lp-mock-txn-icon" style="background:rgba(189,134,106,0.15)">🍕</div>
                <div>
                    <div class="lp-mock-txn-name">Chipotle</div>
                    <div class="lp-mock-txn-date">Today, 1:22 PM</div>
                </div>
            </div>
            <div class="lp-mock-txn-amt neg">-$28</div>
        </div>
        <div class="lp-mock-txn">
            <div class="lp-mock-txn-left">
                <div class="lp-mock-txn-icon" style="background:rgba(189,134,106,0.15)">💼</div>
                <div>
                    <div class="lp-mock-txn-name">Payroll Deposit</div>
                    <div class="lp-mock-txn-date">Oct 1, 9:00 AM</div>
                </div>
            </div>
            <div class="lp-mock-txn-amt pos">+$5,200</div>
        </div>
        <div class="lp-mock-txn">
            <div class="lp-mock-txn-left">
                <div class="lp-mock-txn-icon" style="background:rgba(137,104,95,0.15)">🛒</div>
                <div>
                    <div class="lp-mock-txn-name">Amazon</div>
                    <div class="lp-mock-txn-date">Sep 30, 6:45 PM</div>
                </div>
            </div>
            <div class="lp-mock-txn-amt neg">-$89</div>
        </div>
    </div>
</div>
"""

# ── Budget panel HTML ─────────────────────────────────────────────────────────
BUDGET_PANEL_HTML = """
<div class="lp-panel">
    <div class="lp-panel-header">Monthly Budget Tracker</div>
    <div class="lp-budget-item">
        <div class="lp-budget-row">
            <span class="lp-budget-name">🍔 Food & Dining</span>
            <span class="lp-budget-pct" style="color:#BD866A">68% used</span>
        </div>
        <div class="lp-budget-bg">
            <div class="lp-budget-fill" style="width:68%;background:linear-gradient(90deg,#BD866A,#BD866A)"></div>
        </div>
    </div>
    <div class="lp-budget-item">
        <div class="lp-budget-row">
            <span class="lp-budget-name">🚌 Transport</span>
            <span class="lp-budget-pct" style="color:#BD866A">38% used</span>
        </div>
        <div class="lp-budget-bg">
            <div class="lp-budget-fill" style="width:38%;background:linear-gradient(90deg,#BD866A,#89685F)"></div>
        </div>
    </div>
    <div class="lp-budget-item">
        <div class="lp-budget-row">
            <span class="lp-budget-name">🛍️ Shopping</span>
            <span class="lp-budget-pct" style="color:#89685F">94% used</span>
        </div>
        <div class="lp-budget-bg">
            <div class="lp-budget-fill" style="width:94%;background:linear-gradient(90deg,#BD866A,#89685F)"></div>
        </div>
    </div>
    <div class="lp-budget-item">
        <div class="lp-budget-row">
            <span class="lp-budget-name">🎬 Entertainment</span>
            <span class="lp-budget-pct" style="color:#BD866A">21% used</span>
        </div>
        <div class="lp-budget-bg">
            <div class="lp-budget-fill" style="width:21%;background:linear-gradient(90deg,#BD866A,#d4a080)"></div>
        </div>
    </div>
    <div class="lp-budget-item">
        <div class="lp-budget-row">
            <span class="lp-budget-name">💡 Utilities</span>
            <span class="lp-budget-pct" style="color:#BD866A">45% used</span>
        </div>
        <div class="lp-budget-bg">
            <div class="lp-budget-fill" style="width:45%;background:linear-gradient(90deg,#BD866A,#89685F)"></div>
        </div>
    </div>
    <div style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid rgba(244,236,220,0.06)">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:0.75rem;color:#5c4e46;font-weight:600">Total Spent</span>
            <span style="font-size:0.875rem;font-weight:800;color:#F4ECDC">$1,685 <span style="color:#5c4e46;font-weight:500">/ $3,000</span></span>
        </div>
        <div style="margin-top:8px;height:6px;background:rgba(244,236,220,0.07);border-radius:99px;overflow:hidden">
            <div style="width:55%;height:100%;background:linear-gradient(90deg,#BD866A,#BD866A);border-radius:99px"></div>
        </div>
    </div>
</div>
"""

# ── AI Insights panel HTML ────────────────────────────────────────────────────
INSIGHTS_PANEL_HTML = """
<div class="lp-panel">
    <div class="lp-panel-header">AI Financial Insights</div>
    <div class="lp-insight-card">
        <div class="lp-insight-icon">⚠️</div>
        <div class="lp-insight-text">
            <strong>Dining overspend detected</strong>
            You've eaten out 14 times this month — spending $380 vs your $250 budget.
        </div>
    </div>
    <div class="lp-insight-card">
        <div class="lp-insight-icon">📈</div>
        <div class="lp-insight-text">
            <strong>Savings on track</strong>
            At this pace you'll save $1,840 by month end — $300 above your goal. Great work!
        </div>
    </div>
    <div class="lp-insight-card">
        <div class="lp-insight-icon">💡</div>
        <div class="lp-insight-text">
            <strong>Quick win available</strong>
            Cancelling 2 unused subscriptions ($10/mo each) saves $240 per year.
        </div>
    </div>
    <div style="margin-top:1rem;display:flex;gap:0.75rem">
        <div style="flex:1;background:rgba(189,134,106,0.08);border:1px solid rgba(189,134,106,0.2);border-radius:12px;padding:0.85rem;text-align:center">
            <div style="font-size:1.2rem;font-weight:900;color:#BD866A">78</div>
            <div style="font-size:0.62rem;font-weight:700;color:#5c4e46;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px">Health Score</div>
        </div>
        <div style="flex:1;background:rgba(137,104,95,0.08);border:1px solid rgba(137,104,95,0.2);border-radius:12px;padding:0.85rem;text-align:center">
            <div style="font-size:1.2rem;font-weight:900;color:#d4a080">$1.8k</div>
            <div style="font-size:0.62rem;font-weight:700;color:#5c4e46;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px">Projected Save</div>
        </div>
        <div style="flex:1;background:rgba(189,134,106,0.08);border:1px solid rgba(189,134,106,0.2);border-radius:12px;padding:0.85rem;text-align:center">
            <div style="font-size:1.2rem;font-weight:900;color:#BD866A">3</div>
            <div style="font-size:0.62rem;font-weight:700;color:#5c4e46;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px">Action Items</div>
        </div>
    </div>
</div>
"""


def render() -> None:
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    # ── Handle query-param nav buttons ─────────────────────────────────────────
    if st.query_params.get("show_auth") == "1":
        st.query_params.clear()
        st.session_state.show_auth = True
        st.rerun()

    # ── Navbar (fully self-contained HTML) ─────────────────────────────────────
    st.markdown(
        """
        <div class="lp-nav">
            <div class="lp-nav-logo">
                <div class="lp-nav-logo-icon">
                    <svg width="24" height="22" viewBox="0 0 24 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="0" y="10" width="4" height="12" rx="1" fill="#555"/>
                        <rect x="5.5" y="6" width="4" height="16" rx="1" fill="#888"/>
                        <rect x="11" y="2" width="4" height="20" rx="1" fill="#fff"/>
                        <rect x="16.5" y="0" width="4" height="22" rx="1" fill="#fff"/>
                        <line x1="21" y1="19" x2="23" y2="14" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
                        <circle cx="23" cy="13" r="1.5" fill="#fff"/>
                    </svg>
                </div>
                <div class="lp-nav-logo-text">
                    <span class="lp-nav-logo-name">FinSight</span>
                    <span class="lp-nav-logo-sub">Financial Intelligence</span>
                </div>
            </div>
            <ul class="lp-nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#how-it-works">How it works</a></li>
                <li><a href="#security">Security</a></li>
            </ul>
            <div class="lp-nav-actions">
                <a class="lp-nav-btn-ghost" href="?show_auth=1">Sign In</a>
                <a class="lp-nav-btn-cta"   href="?show_auth=1">Get Started</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Hero ───────────────────────────────────────────────────────────────────
    hero_left, hero_right = st.columns([1, 1], gap="large")
    with hero_left:
        st.markdown(
            """
            <div style="padding:4rem 0 2rem 3rem">
                <div class="lp-hero-badge">✦ AI-POWERED PERSONAL FINANCE</div>
                <h1 class="lp-hero-h1">
                    See exactly where<br>
                    your money <span class="grad">goes every month</span>
                </h1>
                <p class="lp-hero-sub">
                    Upload your bank statement. FinSight AI reads every transaction,
                    builds your spending map, sets smart budgets, and tells you
                    exactly what to change — in seconds.
                </p>
                <div class="lp-hero-social">
                    <div class="lp-hero-social-item">✓&nbsp; No bank login required</div>
                    <div class="lp-hero-social-item">✓&nbsp; Works with any bank</div>
                    <div class="lp-hero-social-item">✓&nbsp; Free to use</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _, h1, _ = st.columns([0.5, 1, 1])
        with h1:
            st.markdown("<div class='lp-btn-primary' style='padding-left:3rem'>", unsafe_allow_html=True)
            if st.button("🚀  Get Started Free", key="hero_cta", use_container_width=True):
                st.session_state.show_auth = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with hero_right:
        st.markdown(
            f"<div style='padding:3rem 3rem 2rem 0'>{MOCKUP_HTML}</div>",
            unsafe_allow_html=True,
        )

    # ── Trusted strip ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="lp-trusted">
            <span class="lp-trusted-label">Trusted security from</span>
            <span class="lp-trusted-item">🔐 Supabase Auth</span>
            <span class="lp-trusted-item">🛡️ Row-Level Security</span>
            <span class="lp-trusted-item">🤖 Google Gemini AI</span>
            <span class="lp-trusted-item">📄 Reducto PDF Engine</span>
            <span class="lp-trusted-item">🔒 256-bit Encryption</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stats bar ──────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding:0 3rem">
            <div class="lp-stats">
                <div class="lp-stat">
                    <div class="lp-stat-val"><span class="accent">PDF</span> → Data</div>
                    <div class="lp-stat-lbl">In Under 10 Seconds</div>
                </div>
                <div class="lp-stat">
                    <div class="lp-stat-val"><span class="accent">Any</span> Bank</div>
                    <div class="lp-stat-lbl">Any Format Worldwide</div>
                </div>
                <div class="lp-stat">
                    <div class="lp-stat-val"><span class="accent">100%</span></div>
                    <div class="lp-stat-lbl">Data Isolated Per User</div>
                </div>
                <div class="lp-stat">
                    <div class="lp-stat-val"><span class="accent">Zero</span></div>
                    <div class="lp-stat-lbl">Manual Entry Needed</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Feature 1: Smart PDF Import ────────────────────────────────────────────
    st.markdown("<div id='features' class='lp-section'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="lp-sec-wrap">
            <div class="lp-sec-tag">FEATURES</div>
            <div class="lp-sec-h2">Everything you need to master your money</div>
            <div class="lp-sec-sub">No spreadsheets. No bank logins. No manual entry. Just drop your PDF and get answers.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feat1_left, feat1_right = st.columns([1, 1], gap="large")
    with feat1_left:
        st.markdown(
            """
            <div style="padding:0 1rem 0 3rem">
                <div class="lp-feat-tag">SMART IMPORT</div>
                <div class="lp-feat-h3">Drop a PDF.<br>Get your full spending picture.</div>
                <p class="lp-feat-p">
                    Export any bank statement as a PDF and upload it. FinSight reads
                    every line using the Reducto AI engine — extracting dates, merchants,
                    and amounts automatically, regardless of your bank's format.
                </p>
                <ul class="lp-feat-bullets">
                    <li>Works with Chase, Bank of America, Wells Fargo, and 100+ banks worldwide</li>
                    <li>Handles multi-page statements with hundreds of transactions</li>
                    <li>Extracts data in seconds — no waiting, no manual mapping</li>
                    <li>PDF never stored — processed and discarded immediately</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with feat1_right:
        st.markdown(
            f"<div style='padding:0 3rem 0 1rem'>{MOCKUP_HTML}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Feature 2: Budget Tracking ─────────────────────────────────────────────
    st.markdown("<div class='lp-section-alt'>", unsafe_allow_html=True)
    feat2_left, feat2_right = st.columns([1, 1], gap="large")
    with feat2_left:
        st.markdown(
            f"<div style='padding:2rem 1rem 2rem 3rem'>{BUDGET_PANEL_HTML}</div>",
            unsafe_allow_html=True,
        )
    with feat2_right:
        st.markdown(
            """
            <div style="padding:2rem 3rem 2rem 1rem">
                <div class="lp-feat-tag">BUDGET MANAGEMENT</div>
                <div class="lp-feat-h3">Set budgets that actually stick.</div>
                <p class="lp-feat-p">
                    FinSight analyses your past spending, suggests smart monthly budgets
                    per category, and tracks your progress in real time — so you always
                    know if you're on track before it's too late.
                </p>
                <ul class="lp-feat-bullets">
                    <li>AI-suggested budgets based on your spending history</li>
                    <li>Visual progress bars per category — Food, Transport, Shopping and more</li>
                    <li>Alerts when you're approaching your limit</li>
                    <li>Month-over-month comparison to spot trends</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Feature 3: AI Insights ─────────────────────────────────────────────────
    st.markdown("<div class='lp-section'>", unsafe_allow_html=True)
    feat3_left, feat3_right = st.columns([1, 1], gap="large")
    with feat3_left:
        st.markdown(
            """
            <div style="padding:2rem 1rem 2rem 3rem">
                <div class="lp-feat-tag">AI INSIGHTS</div>
                <div class="lp-feat-h3">Your personal finance advisor — on demand.</div>
                <p class="lp-feat-p">
                    Ask FinSight anything about your money. "Where did I overspend last month?"
                    "How much did I spend on food vs transport?" Get intelligent, specific answers
                    powered by Google Gemini — not generic tips.
                </p>
                <ul class="lp-feat-bullets">
                    <li>Chat with your financial data in plain English</li>
                    <li>Spending health score updated monthly</li>
                    <li>Detects unusual spikes and recurring subscriptions</li>
                    <li>End-of-month savings predictions based on current pace</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with feat3_right:
        st.markdown(
            f"<div style='padding:2rem 3rem 2rem 1rem'>{INSIGHTS_PANEL_HTML}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── How it works ───────────────────────────────────────────────────────────
    st.markdown("<div id='how-it-works' class='lp-section-alt'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="lp-sec-wrap">
            <div class="lp-sec-tag">HOW IT WORKS</div>
            <div class="lp-sec-h2">From PDF to insights in 3 steps</div>
            <div class="lp-sec-sub">No setup. No bank linking. No waiting. Just results.</div>
        </div>
        <div class="lp-steps">
            <div class="lp-step">
                <div class="lp-step-num">1</div>
                <div class="lp-step-title">Upload your bank statement</div>
                <div class="lp-step-desc">
                    Export a PDF from your bank app or internet banking.
                    Drag and drop it into FinSight — any bank, any format.
                </div>
            </div>
            <div class="lp-step">
                <div class="lp-step-num">2</div>
                <div class="lp-step-title">AI reads and categorises</div>
                <div class="lp-step-desc">
                    FinSight AI extracts every transaction and categorises it —
                    Food, Transport, Shopping, Utilities — in seconds.
                </div>
            </div>
            <div class="lp-step">
                <div class="lp-step-num">3</div>
                <div class="lp-step-title">Get your insights &amp; act</div>
                <div class="lp-step-desc">
                    Review your spending score, chat with your data, set budgets,
                    and get specific tips to save more next month.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Testimonials ───────────────────────────────────────────────────────────
    st.markdown("<div class='lp-section'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="lp-sec-wrap">
            <div class="lp-sec-tag">TESTIMONIALS</div>
            <div class="lp-sec-h2">Loved by people who want clarity on their money</div>
        </div>
        <div class="lp-testimonials">
            <div class="lp-tcard">
                <div class="lp-tcard-stars">★★★★★</div>
                <div class="lp-tcard-quote">
                    "I had no idea I was spending $400 a month on food delivery.
                    FinSight showed me in 30 seconds. I've already cut it in half."
                </div>
                <div class="lp-tcard-author">
                    <div class="lp-tcard-avatar" style="background:linear-gradient(135deg,#BD866A,#89685F)">A</div>
                    <div>
                        <div class="lp-tcard-name">Alex Morgan</div>
                        <div class="lp-tcard-role">Software Engineer, Austin, TX</div>
                    </div>
                </div>
            </div>
            <div class="lp-tcard">
                <div class="lp-tcard-stars">★★★★★</div>
                <div class="lp-tcard-quote">
                    "Finally a finance app that doesn't ask for my bank password.
                    I upload my Chase statement and get a full breakdown instantly. Brilliant."
                </div>
                <div class="lp-tcard-author">
                    <div class="lp-tcard-avatar" style="background:linear-gradient(135deg,#89685F,#c4906e)">P</div>
                    <div>
                        <div class="lp-tcard-name">Patricia Lee</div>
                        <div class="lp-tcard-role">Product Manager, New York, NY</div>
                    </div>
                </div>
            </div>
            <div class="lp-tcard">
                <div class="lp-tcard-stars">★★★★★</div>
                <div class="lp-tcard-quote">
                    "The AI chat feature is incredible. I asked 'where did I overspend'
                    and got specific suggestions instantly. Like having a financial advisor in my pocket."
                </div>
                <div class="lp-tcard-author">
                    <div class="lp-tcard-avatar" style="background:linear-gradient(135deg,#4F494C,#89685F)">R</div>
                    <div>
                        <div class="lp-tcard-name">Ryan Davis</div>
                        <div class="lp-tcard-role">Freelance Designer, Chicago, IL</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Security section ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div id="security" style="padding:0 3rem 3rem">
            <div class="lp-security">
                <div class="lp-sec-item">
                    <div class="lp-sec-icon">🔐</div>
                    <div class="lp-sec-title-sm">End-to-End Encryption</div>
                    <div class="lp-sec-desc">All data encrypted in transit and at rest using AES-256.</div>
                </div>
                <div class="lp-sec-item">
                    <div class="lp-sec-icon">👤</div>
                    <div class="lp-sec-title-sm">Row-Level Security</div>
                    <div class="lp-sec-desc">Your data is completely isolated. No other user can ever access it.</div>
                </div>
                <div class="lp-sec-item">
                    <div class="lp-sec-icon">🚫</div>
                    <div class="lp-sec-title-sm">No PDF Storage</div>
                    <div class="lp-sec-desc">Your bank statement is processed and discarded immediately — never stored.</div>
                </div>
                <div class="lp-sec-item">
                    <div class="lp-sec-icon">🛡️</div>
                    <div class="lp-sec-title-sm">No Data Sharing</div>
                    <div class="lp-sec-desc">We never sell or share your financial data with any third party. Ever.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Bottom CTA banner ──────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="lp-cta-banner">
            <div class="lp-cta-h2">Ready to take control of your money?</div>
            <p class="lp-cta-sub">Join thousands of people who finally understand where their money goes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, cta_mid, _ = st.columns([2, 1, 2])
    with cta_mid:
        st.markdown("<div class='lp-cta-btn-wrap' style='margin-top:1.25rem'>", unsafe_allow_html=True)
        if st.button("🚀  Get Started — It's Free", key="bottom_cta", use_container_width=True):
            st.session_state.show_auth = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="lp-footer">
            <div class="lp-footer-logo">💡 FinSight</div>
            <div class="lp-footer-links">
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Security</a>
                <a href="#">Contact</a>
            </div>
            <div class="lp-footer-copy">© 2024 FinSight. All rights reserved.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
