import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "cases.db"


@st.cache_data
def load_case_data() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    query = "SELECT case_name, neutral_citation, judge, court, decision_date, parties, keywords, content FROM cases"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


st.set_page_config(page_title="UK Legal Data Explorer", page_icon="⚖️", layout="wide")
st.title("UK Public Legal Data Explorer")

if not DB_PATH.exists():
    st.warning("Database not found. Run `python scripts/ingest.py` and `python scripts/load.py` first.")
    st.stop()

all_cases = load_case_data()

st.sidebar.header("Filters")
judge_filter = st.sidebar.text_input("Judge")
court_filter = st.sidebar.text_input("Court")
keyword_filter = st.sidebar.text_input("Keyword")

filtered = all_cases.copy()
if judge_filter:
    filtered = filtered[filtered["judge"].str.contains(judge_filter, case=False, na=False)]
if court_filter:
    filtered = filtered[filtered["court"].str.contains(court_filter, case=False, na=False)]
if keyword_filter:
    filtered = filtered[filtered["keywords"].fillna("").str.contains(keyword_filter, case=False, na=False)]

st.metric("Cases shown", len(filtered))

if filtered.empty:
    st.info("No matching cases were found for the selected filters.")
else:
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.subheader("Case details")
    selected_case = st.selectbox(
        "Choose a case to inspect",
        options=filtered["case_name"].tolist(),
    )

    case = filtered[filtered["case_name"] == selected_case].iloc[0]
    st.write(f"**Case name:** {case['case_name']}")
    st.write(f"**Neutral citation:** {case['neutral_citation']}")
    st.write(f"**Judge:** {case['judge']}")
    st.write(f"**Court:** {case['court']}")
    st.write(f"**Decision date:** {case['decision_date']}")
    st.write(f"**Parties:** {case['parties']}")
    st.write(f"**Keywords:** {case['keywords']}")
    st.write("**Summary:**")
    st.write(case["content"])
