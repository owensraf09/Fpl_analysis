import streamlit as st
import requests
import pandas as pd
from data import df, teams


st.title("Fixture Difficulty Heatmap")
st.markdown("Upcoming fixture difficulty for every Premier League team across the next gameweeks.")
st.divider()

# --- FDR colour mapping ---
# FDR 1-2 = easy (green), 3 = medium (yellow), 4-5 = hard (red)
FDR_COLOURS = {
    1: ("background-color: #257a3e; color: #ffffff;", "1"),
    2: ("background-color: #00ff86; color: #000000;", "2"),
    3: ("background-color: #ebebe4; color: #000000;", "3"),
    4: ("background-color: #ff1751; color: #ffffff;", "4"),
    5: ("background-color: #80072d; color: #ffffff;", "5"),
}

@st.cache_data(ttl=3600)
def fetch_fixtures_and_teams():
    bootstrap = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    fixtures  = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()

    team_map = {t["id"]: t["short_name"] for t in bootstrap["teams"]}
    current_gw = next(
        (e["id"] for e in bootstrap["events"] if e["is_current"]),
        next((e["id"] for e in bootstrap["events"] if e["is_next"]), 1)
    )

    return fixtures, team_map, current_gw

try:
    fixtures, team_map, current_gw = fetch_fixtures_and_teams()
except Exception as e:
    st.error(f"Could not load fixture data: {e}")
    st.stop()

# --- Controls ---
col_a, col_b = st.columns([1, 3])
with col_a:
    num_gws = st.slider("Gameweeks to show", min_value=3, max_value=10, value=6)

gw_range = list(range(current_gw + 1, current_gw + 1 + num_gws))

# --- Build fixture grid ---
# For each team, for each GW, find their opponent and FDR
rows = {}
for fixture in fixtures:
    gw = fixture.get("event")
    if gw not in gw_range:
        continue
    if fixture.get("finished_provisional") or fixture.get("started"):
        continue

    home_id = fixture["team_h"]
    away_id = fixture["team_a"]
    home_fdr = fixture["team_h_difficulty"]
    away_fdr = fixture["team_a_difficulty"]
    home_name = team_map.get(home_id, "?")
    away_name = team_map.get(away_id, "?")

    # Home team entry
    if home_id not in rows:
        rows[home_id] = {"Team": home_name}
    gw_key = f"GW{gw}"
    existing = rows[home_id].get(gw_key)
    new_entry = (f"{away_name} (H)", home_fdr)
    rows[home_id][gw_key] = [existing, new_entry] if existing else new_entry

    # Away team entry
    if away_id not in rows:
        rows[away_id] = {"Team": away_name}
    existing = rows[away_id].get(gw_key)
    new_entry = (f"{home_name} (A)", away_fdr)
    rows[away_id][gw_key] = [existing, new_entry] if existing else new_entry

# Fill blanks for BGW teams
gw_cols = [f"GW{gw}" for gw in gw_range]
for team_id, row in rows.items():
    for col in gw_cols:
        if col not in row:
            row[col] = None

grid_df = pd.DataFrame(list(rows.values())).set_index("Team").sort_index()
grid_df = grid_df[gw_cols]

# --- Render HTML heatmap ---
def fdr_cell(value):
    if value is None:
        return '<td style="background-color:#1e1e1e; color:#555; text-align:center; padding:8px 12px; font-size:0.8rem;">—</td>'

    # Handle double gameweeks (list of two fixtures)
    if isinstance(value, list):
        cells = ""
        for v in value:
            if v:
                label, fdr = v
                style, _ = FDR_COLOURS.get(fdr, ("background-color:#333; color:#fff;", str(fdr)))
                cells += f'<div style="{style} padding:3px 6px; border-radius:3px; margin:2px; font-size:0.75rem; font-weight:600; white-space:nowrap;">{label}</div>'
        return f'<td style="text-align:center; padding:4px 8px;">{cells}</td>'

    label, fdr = value
    style, _ = FDR_COLOURS.get(fdr, ("background-color:#333; color:#fff;", str(fdr)))
    return f'<td style="{style} text-align:center; padding:8px 12px; font-size:0.8rem; font-weight:600; white-space:nowrap;">{label}</td>'

html = '<table style="border-collapse:collapse; width:100%; font-family: sans-serif;">'

# Header row
html += '<thead><tr>'
html += '<th style="text-align:left; padding:8px 12px; background:#1e1e1e; color:#aaa; font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase; position:sticky; left:0;">Team</th>'
for col in gw_cols:
    html += f'<th style="text-align:center; padding:8px 12px; background:#1e1e1e; color:#aaa; font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase;">{col}</th>'
html += '</tr></thead>'

# Data rows
html += '<tbody>'
for i, (team, row) in enumerate(grid_df.iterrows()):
    bg = "#141414" if i % 2 == 0 else "#1a1a1a"
    html += f'<tr style="background:{bg};">'
    html += f'<td style="padding:8px 12px; font-size:0.85rem; font-weight:600; color:#e2e5ed; background:{bg}; position:sticky; left:0; white-space:nowrap;">{team}</td>'
    for col in gw_cols:
        html += fdr_cell(row[col])
    html += '</tr>'
html += '</tbody></table>'

st.markdown(html, unsafe_allow_html=True)

st.divider()

# --- Legend ---
st.markdown("**Difficulty Rating**")
legend_cols = st.columns(5)
labels = {1: "1 — Very Easy", 2: "2 — Easy", 3: "3 — Medium", 4: "4 — Hard", 5: "5 — Very Hard"}
for i, (fdr, (style, _)) in enumerate(FDR_COLOURS.items()):
    with legend_cols[i]:
        st.markdown(
            f'<div style="{style} padding:6px 10px; border-radius:4px; text-align:center; font-size:0.8rem; font-weight:600;">{labels[fdr]}</div>',
            unsafe_allow_html=True
        )