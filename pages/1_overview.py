import streamlit as st
import pandas as pd
from data import df, top_10, tdf, total_players, avg_points, top_scorer, top_scorer_pts, most_selected, most_selected_pct

st.set_page_config(page_title="FPL Dashboard", layout="wide")


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