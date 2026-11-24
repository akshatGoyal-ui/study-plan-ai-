import pandas as pd
import streamlit as st

from modules.evaluation import run_scenarios
from modules.ui import apply_style, page_heading

apply_style()
page_heading("Testing & evaluation", "Twelve executable scenarios exercise Python input and timetable validation logic.")
st.info("These are automated deterministic validation tests. Subjective AI quality (clarity, usefulness, and model adherence) is not scored here and needs real model outputs plus human review.")
results = run_scenarios()
frame = pd.DataFrame(results)
passed = int((frame["Pass/Fail"] == "PASS").sum())
failed = len(frame) - passed
c1, c2, c3 = st.columns(3)
c1.metric("Scenarios executed", len(frame))
c2.metric("Passed", passed)
c3.metric("Failed", failed)
st.dataframe(frame, hide_index=True, width="stretch", column_config={"Input": st.column_config.TextColumn(width="large"), "Expected Output": st.column_config.TextColumn(width="large"), "Actual Output": st.column_config.TextColumn(width="large")})
st.download_button("Download scenario results CSV", frame.to_csv(index=False).encode("utf-8-sig"), "studyplan_test_results.csv", "text/csv", type="primary")
