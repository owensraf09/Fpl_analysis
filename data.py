import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
FIXTURES_URL = "https://fantasy.premierleague.com/api/fixtures/"

DIFFICULTY_LABEL = {1: "Very Easy", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Very Hard"}

# --- Fetch core data ---
stats = requests.get(BASE_URL).json()
fixtures = requests.get(FIXTURES_URL).json()

elements = pd.DataFrame(stats["elements"])
teams = pd.DataFrame(stats["teams"])
positions = pd.DataFrame(stats["element_types"])

teams["id"] = teams["id"].astype(int)

# --- Merged main dataframe ---
df = pd.merge(elements, teams, left_on="team", right_on="id")
df = pd.merge(df, positions, left_on="element_type", right_on="id")

# --- Top 10 players by total points ---
top_10 = df[["web_name", "name", "singular_name", "total_points", "now_cost", "selected_by_percent"]].copy()
top_10 = top_10.rename(columns={
    "name": "Team",
    "singular_name": "Position",
    "web_name": "Player",
    "total_points": "Total Points",
    "now_cost": "Cost (£)",
    "selected_by_percent": "Selected By (%)"
})
top_10["Cost (£)"] = top_10["Cost (£)"] / 10
top_10 = top_10.sort_values("Total Points", ascending=False).head(10)
top_10.reset_index(drop=True, inplace=True)
top_10.index += 1

# --- Team strength table ---
tdf = teams[[
    "name", "position", "strength",
    "strength_overall_home", "strength_overall_away",
    "strength_attack_home", "strength_attack_away",
    "strength_defence_home", "strength_defence_away"
]].sort_values("position").copy()
tdf = tdf.rename(columns={
    "name": "Team",
    "position": "League Position",
    "strength": "Strength",
    "strength_overall_home": "Overall Home",
    "strength_overall_away": "Overall Away",
    "strength_attack_home": "Attack Home",
    "strength_attack_away": "Attack Away",
    "strength_defence_home": "Defence Home",
    "strength_defence_away": "Defence Away",
})
tdf.set_index("League Position", inplace=True)

# --- Summary stats ---
total_players = len(elements)
avg_points = round(elements["total_points"].mean(), 1)
top_scorer = df.loc[df["total_points"].idxmax(), "web_name"]
top_scorer_pts = int(df["total_points"].max())
most_selected = df.loc[df["selected_by_percent"].astype(float).idxmax(), "web_name"]
most_selected_pct = df["selected_by_percent"].astype(float).max()