import streamlit as st

st.set_page_config(page_title="FPL Dashboard", layout="wide")

overview = st.Page("pages/1_Overview.py", title="Overview")
my_team = st.Page("pages/2_My_Team.py", title="My Team Analysis")

pg = st.navigation([overview, my_team])
pg.run()