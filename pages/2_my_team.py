import streamlit as st
import requests
import pandas as pd
from data import df, teams, positions



st.title("Team Analysis")
st.markdown("Enter your FPL Team ID below to load your squad and get personalised insights.")

st.info(
    "Find your Team ID: Log into the FPL website, click on your squad name, "
    "and look at the URL — the number after `/entry/` is your Team ID.",
)

# --- Team ID Input ---
team_id_input = st.text_input(
    "Enter your FPL Team ID",
    placeholder="e.g. 1234567"
)
submitted = st.button("Submit")

team_id = None
if submitted and team_id_input.strip():
    try:
        team_id = int(team_id_input.strip())
    except ValueError:
        st.error("Please enter a valid numeric Team ID.")

if team_id:
    with st.spinner("Fetching your team data..."):
        try:
            team_url = f"https://fantasy.premierleague.com/api/entry/{int(team_id)}/"
            team_resp = requests.get(team_url)
            team_resp.raise_for_status()
            team_info = team_resp.json()

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

    # 'form' may be suffixed to 'form_x' or 'form_y' after a DataFrame merge
    form_col = next(
        (c for c in ["form", "form_x", "form_y"] if c in squad_df.columns),
        None
    )

    base_cols = [
        "id_x", "web_name", "name", "singular_name",
        "total_points", "now_cost",
        "goals_scored", "assists", "clean_sheets",
        "minutes", "yellow_cards", "red_cards", "selected_by_percent"
    ]
    if form_col:
        base_cols.insert(6, form_col)

    squad_df = squad_df[base_cols].copy()

    rename_map = {
        "id_x": "id",
        "web_name": "Player",
        "name": "Team",
        "singular_name": "Position",
        "total_points": "Total Pts",
        "now_cost": "Cost (£)",
        "goals_scored": "Goals",
        "assists": "Assists",
        "clean_sheets": "Clean Sheets",
        "minutes": "Minutes",
        "yellow_cards": "Yellows",
        "red_cards": "Reds",
        "selected_by_percent": "Ownership (%)"
    }
    if form_col:
        rename_map[form_col] = "Form"

    squad_df = squad_df.rename(columns=rename_map)

    squad_df["Cost (£)"] = squad_df["Cost (£)"] / 10
    squad_df["Captain"] = squad_df["id"].map(lambda x: "C" if is_captain.get(x) else ("V" if is_vice.get(x) else ""))
    squad_df["Multiplier"] = squad_df["id"].map(multipliers)

    pos_order = {"Goalkeeper": 1, "Defender": 2, "Midfielder": 3, "Forward": 4}
    squad_df["pos_order"] = squad_df["Position"].map(pos_order)
    squad_df = squad_df.sort_values(["Multiplier", "pos_order"], ascending=[False, True])
    squad_df = squad_df.drop(columns=["id", "pos_order", "Multiplier"])
    squad_df.reset_index(drop=True, inplace=True)
    squad_df.index += 1

    col_config = {
        "Cost (£)": st.column_config.NumberColumn(format="£%.1f"),
        "Ownership (%)": st.column_config.NumberColumn(format="%.1f%%"),
    }
    if "Form" in squad_df.columns:
        col_config["Form"] = st.column_config.NumberColumn(format="%.1f")

    st.dataframe(squad_df, use_container_width=True, column_config=col_config)

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
        chip_names = {
            "wildcard": "Wildcard",
            "freehit":  "Free Hit",
            "bboost":   "Bench Boost",
            "3xc":      "Triple Captain",
        }

        def calc_chip_gain(chip_code, gw):
            try:
                gw_picks = requests.get(f"https://fantasy.premierleague.com/api/entry/{int(team_id)}/event/{gw}/picks/").json().get("picks", [])
                pts_map = {el["id"]: el["stats"]["total_points"] for el in requests.get(f"https://fantasy.premierleague.com/api/event/{gw}/live/").json().get("elements", [])}

                if chip_code == "bboost":
                    return sum(pts_map.get(p["element"], 0) for p in gw_picks if p["position"] > 11)

                if chip_code == "3xc":
                    captain = next((p for p in gw_picks if p["is_captain"]), None)
                    return pts_map.get(captain["element"], 0) if captain else 0

            except Exception:
                pass
            return None

        rows = []
        for chip in chips:
            code = chip["name"]
            gw   = chip["event"]
            name = chip_names.get(code, code)
            gain = "N/A" if code in ("wildcard", "freehit") else (calc_chip_gain(code, gw) or "N/A")
            rows.append({"Chip": name, "Gameweek Used": gw, "Points Gained": gain})

        chips_df = pd.DataFrame(rows)
        st.dataframe(chips_df, use_container_width=True)
    else:
        st.info("No chips used yet this season.")