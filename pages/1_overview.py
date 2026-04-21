import streamlit as st
import pandas as pd
from data import df, top_10, tdf, total_players, avg_points, top_scorer, top_scorer_pts, most_selected, most_selected_pct

st.set_page_config(page_title="FPL Dashboard", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

/* ── Root tokens ── */
:root {
    --pl-purple:   #37003c;
    --pl-gold:     #e8a730;
    --pl-green:    #00ff85;
    --pl-white:    #f0eef2;
    --pl-muted:    #9b8fa0;
    --pl-card-bg:  #4a1a52;
    --pl-border:   #6b2d75;
    --pl-hover:    #5c2264;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    color: var(--pl-white);
}

.stApp {
    background-color: var(--pl-purple);
    background-image:
        radial-gradient(ellipse at 0% 0%, rgba(232,167,48,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 100% 100%, rgba(0,255,133,0.05) 0%, transparent 55%);
}

/* ── Top bar / toolbar ── */
header[data-testid="stHeader"] {
    background-color: var(--pl-purple);
    border-bottom: 2px solid var(--pl-gold);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #2a0030;
    border-right: 1px solid var(--pl-border);
}
section[data-testid="stSidebar"] * {
    color: var(--pl-white) !important;
}

/* ── Main title ── */
h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.8rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: var(--pl-white) !important;
    border-left: 5px solid var(--pl-gold);
    padding-left: 1rem;
    margin-bottom: 0.25rem !important;
}

h2, h3 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--pl-white) !important;
}

p, .stMarkdown p {
    color: var(--pl-muted) !important;
    font-size: 0.95rem;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--pl-border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--pl-card-bg);
    border: 1px solid var(--pl-border);
    border-top: 3px solid var(--pl-gold);
    border-radius: 6px;
    padding: 1.1rem 1.2rem !important;
    transition: background 0.2s;
}
[data-testid="stMetric"]:hover {
    background: var(--pl-hover);
}

[data-testid="stMetricLabel"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--pl-muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--pl-white) !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.85rem !important;
    color: var(--pl-green) !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"],
iframe {
    border: 1px solid var(--pl-border) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p,
small {
    color: var(--pl-muted) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.03em;
}

/* ── Subheader accent line ── */
h3::after {
    content: '';
    display: block;
    width: 3rem;
    height: 3px;
    background: var(--pl-gold);
    margin-top: 0.4rem;
    border-radius: 2px;
}

/* ── Number input & widgets ── */
input[type="number"], .stNumberInput input {
    background-color: var(--pl-card-bg) !important;
    border: 1px solid var(--pl-border) !important;
    color: var(--pl-white) !important;
    border-radius: 4px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--pl-gold) !important;
}

/* ── Alert / info boxes ── */
[data-testid="stAlert"] {
    background-color: var(--pl-card-bg) !important;
    border: 1px solid var(--pl-gold) !important;
    border-radius: 6px !important;
    color: var(--pl-white) !important;
}

/* ── Bar/line charts ── */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: var(--pl-card-bg) !important;
    border: 1px solid var(--pl-border) !important;
    border-radius: 6px !important;
    padding: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("Fantasy Premier League Dashboard")
st.markdown("Live data powered by the official FPL API.")
st.divider()

# --- Summary Metric Cards ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Players", f"{total_players:,}")
col2.metric("Avg. Points Per Player", avg_points)
col3.metric("Top Scorer", top_scorer, f"{top_scorer_pts} pts")
col4.metric("Most Selected", most_selected, f"{most_selected_pct}%")

st.divider()

# --- Top 10 Players ---
st.subheader("Top 10 Players by Total Points")
st.dataframe(
    top_10,
    use_container_width=True,
    column_config={
        "Cost (£)": st.column_config.NumberColumn(format="£%.1f"),
        "Selected By (%)": st.column_config.NumberColumn(format="%.1f%%"),
        "Total Points": st.column_config.NumberColumn(format="%d pts"),
    }
)

st.divider()

# --- Team Strength Table ---
st.subheader("Premier League Team Strengths")
st.caption("Strength ratings are provided by FPL and reflect team quality across home/away contexts.")
st.dataframe(tdf, use_container_width=True)
