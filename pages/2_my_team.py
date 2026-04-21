import streamlit as st
import requests
import pandas as pd
from data import df, teams, positions

st.set_page_config(page_title="My Team | FPL Dashboard", layout="wide")

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

/* ── Top bar ── */
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

/* ── Headings ── */
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

h3::after {
    content: '';
    display: block;
    width: 3rem;
    height: 3px;
    background: var(--pl-gold);
    margin-top: 0.4rem;
    border-radius: 2px;
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

/* ── Number input ── */
[data-testid="stNumberInput"] input,
input[type="number"] {
    background-color: var(--pl-card-bg) !important;
    border: 1px solid var(--pl-border) !important;
    border-radius: 4px !important;
    color: var(--pl-white) !important;
    font-family: 'Barlow', sans-serif !important;
}
[data-testid="stNumberInput"] label {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--pl-muted) !important;
}

/* ── Alert / info boxes ── */
[data-testid="stAlert"] {
    background-color: var(--pl-card-bg) !important;
    border: 1px solid var(--pl-gold) !important;
    border-left: 4px solid var(--pl-gold) !important;
    border-radius: 6px !important;
    color: var(--pl-white) !important;
}
[data-testid="stAlert"] p {
    color: var(--pl-white) !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"],
iframe {
    border: 1px solid var(--pl-border) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── Bar/line charts ── */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: var(--pl-card-bg) !important;
    border: 1px solid var(--pl-border) !important;
    border-radius: 6px !important;
    padding: 0.75rem;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--pl-gold) !important;
}

/* ── Caption / small text ── */
[data-testid="stCaptionContainer"] p,
small {
    color: var(--pl-muted) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.03em;
}

/* ── Inline bold in markdown ── */
strong {
    color: var(--pl-white) !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Team Analysis")
st.markdown("Enter your FPL Team ID below to load your squad and get personalised insights.")

st.info(
    "Find your Team ID: Log into the FPL website, click on your squad name, "
    "and look at the URL — the number after `/entry/` is your Team ID.",
)

# --- Team ID Input ---
team_id = st.number_input(
    "Enter your FPL Team ID",
    min_value=1,
    step=1,
    value=None,
    placeholder="e.g. 1234567",
    format="%d"
)

if team_id:
    with st.spinner("Fetching your team data..."):
        try:
            # Fetch team info
            team_url = f"https://fantasy.premierleague.com/api/entry/{int(team_id)}/"
            team_resp = requests.get(team_url)
            team_resp.raise_for_status()
            team_info = team_resp.json()

            # Fetch current picks (latest GW)
            current_gw = team_info.get("current_event")
            if not current_gw:
                st.error("No gameweek data found for this team. Have they made any transfers yet?")
                st.stop()

            picks_url = f"https://fantasy.premierleague.com/api/entry/{int(team_id)}/event/{current_gw}/picks/"
            picks_resp = requests.get(picks_url)
            picks_resp.raise_for_status()
            picks_data = picks_resp.json()

            history_url = f"https://fantasy.premierleague.com/api/entry/{int(team_id)}/history/"
            history_resp = requests.get(history_url)
            history_resp.raise_for_status()
            history_data = history_resp.json()

        except requests.exceptions.HTTPError:
            st.error("Team not found. Please double-check your Team ID.")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    # --- Team Header ---
    st.divider()
    manager_name = f"{team_info.get('player_first_name', '')} {team_info.get('player_last_name', '')}".strip()
    team_name = team_info.get("name", "Unknown Team")
    overall_rank = team_info.get("summary_overall_rank")
    overall_points = team_info.get("summary_overall_points")
    gw_points = team_info.get("summary_event_points")
    gw_rank = team_info.get("summary_event_rank")

    st.subheader(f"{team_name}")
    st.caption(f"Manager: {manager_name}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Points", f"{overall_points:,}" if overall_points else "N/A")
    c2.metric("Overall Rank", f"{overall_rank:,}" if overall_rank else "N/A")
    c3.metric(f"GW{current_gw} Points", gw_points if gw_points else "N/A")
    c4.metric(f"GW{current_gw} Rank", f"{gw_rank:,}" if gw_rank else "N/A")

    st.divider()

    # --- Squad Breakdown ---
    st.subheader("Current Squad")

    picks = picks_data.get("picks", [])
    player_ids = [p["element"] for p in picks]
    multipliers = {p["element"]: p["multiplier"] for p in picks}
    is_captain = {p["element"]: p["is_captain"] for p in picks}
    is_vice = {p["element"]: p["is_vice_captain"] for p in picks}

    squad_df = df[df["id_x"].isin(player_ids)].copy()
    squad_df = squad_df[[
        "id_x", "web_name", "name", "singular_name",
        "total_points", "now_cost", "form",
        "goals_scored", "assists", "clean_sheets",
        "minutes", "yellow_cards", "red_cards", "selected_by_percent"
    ]].copy()

    squad_df = squad_df.rename(columns={
        "id_x": "id",
        "web_name": "Player",
        "name": "Team",
        "singular_name": "Position",
        "total_points": "Total Pts",
        "now_cost": "Cost (£)",
        "form": "Form",
        "goals_scored": "Goals",
        "assists": "Assists",
        "clean_sheets": "Clean Sheets",
        "minutes": "Minutes",
        "yellow_cards": "Yellows",
        "red_cards": "Reds",
        "selected_by_percent": "Ownership (%)"
    })

    squad_df["Cost (£)"] = squad_df["Cost (£)"] / 10
    squad_df["Captain"] = squad_df["id"].map(lambda x: "C" if is_captain.get(x) else ("V" if is_vice.get(x) else ""))
    squad_df["Multiplier"] = squad_df["id"].map(multipliers)

    # Position order
    pos_order = {"Goalkeeper": 1, "Defender": 2, "Midfielder": 3, "Forward": 4}
    squad_df["pos_order"] = squad_df["Position"].map(pos_order)
    squad_df = squad_df.sort_values(["Multiplier", "pos_order"], ascending=[False, True])
    squad_df = squad_df.drop(columns=["id", "pos_order", "Multiplier"])
    squad_df.reset_index(drop=True, inplace=True)
    squad_df.index += 1

    st.dataframe(
        squad_df,
        use_container_width=True,
        column_config={
            "Cost (£)": st.column_config.NumberColumn(format="£%.1f"),
            "Ownership (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Form": st.column_config.NumberColumn(format="%.1f"),
        }
    )

    st.divider()

    # --- Points per Position ---
    st.subheader("Points by Position")
    pos_points = squad_df.groupby("Position")["Total Pts"].sum().reset_index()
    pos_points = pos_points.sort_values("Total Pts", ascending=False)
    st.bar_chart(pos_points.set_index("Position")["Total Pts"])

    st.divider()

    # --- GW Points History ---
    st.subheader("Gameweek Points History")
    gw_history = history_data.get("current", [])
    if gw_history:
        hist_df = pd.DataFrame(gw_history)[["event", "points", "overall_rank", "total_points"]].copy()
        hist_df = hist_df.rename(columns={
            "event": "Gameweek",
            "points": "GW Points",
            "overall_rank": "Overall Rank",
            "total_points": "Total Points"
        })
        hist_df = hist_df.set_index("Gameweek")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**GW Points Per Week**")
            st.line_chart(hist_df["GW Points"])
        with col_b:
            st.markdown("**Cumulative Total Points**")
            st.line_chart(hist_df["Total Points"])
    else:
        st.info("No gameweek history available yet.")

    st.divider()

    # --- Chips Used ---
    st.subheader("Chips Used")
    chips = history_data.get("chips", [])
    if chips:
        chips_df = pd.DataFrame(chips)[["name", "event"]].rename(columns={"name": "Chip", "event": "Gameweek Used"})
        st.dataframe(chips_df, use_container_width=True)
    else:
        st.info("No chips used yet this season.")
