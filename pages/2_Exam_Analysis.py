from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.priority_analyzer import analyze_subjects, score_formula
from modules.ui import apply_style, get_profile, page_heading

apply_style()
page_heading("Exam & subject analysis", "See how exam proximity, difficulty, and your chosen priority shape study attention.")
profile = get_profile()
subjects = profile.get("subjects", [])
if not subjects:
    st.info("Add subjects and exam dates on the Student Information page to see the analysis.")
else:
    analyzed = analyze_subjects(subjects)
    if not analyzed:
        st.warning("No subjects have a valid exam date yet. Return to Student Information and add valid dates.")
    else:
        rows = []
        for subject in analyzed:
            days = subject["days_remaining"]
            available_days = [date.today() + timedelta(days=i) for i in range(max(0, days)) if (date.today() + timedelta(days=i)).strftime("%A") in profile.get("study_days", [])]
            rows.append({"Subject": subject["name"], "Exam date": subject["exam_date_parsed"].isoformat(), "Days remaining": max(0, days), "Difficulty": subject.get("difficulty", "Medium"), "Your priority": subject.get("priority", "Medium"), "Available study days": len(available_days), "Estimated available hours": round(len(available_days) * float(profile.get("daily_hours", 0) or 0), 1), "Priority score": subject["priority_score"]})
        table = pd.DataFrame(rows)
        st.dataframe(table, hide_index=True, width="stretch")
        urgent = analyzed[0]
        st.success(f"**Needs closest attention:** {urgent['name']} — {max(0, urgent['days_remaining'])} day(s) until its exam; score {urgent['priority_score']:.2f}/10.")
        with st.expander("How the score is calculated"):
            st.write(score_formula())
            st.caption("This score is a transparent Python calculation, not an AI-generated judgment. It is a planning aid, not a prediction of exam performance.")
        chart = px.bar(table.sort_values("Priority score"), x="Priority score", y="Subject", orientation="h", color="Priority score", color_continuous_scale=["#b9dfe1", "#087e8b"], range_x=[0, 10])
        chart.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=12, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, width="stretch")
        st.caption("Estimated available preparation hours = selected study days before the exam × daily study-hour limit. Commitments and rest are not subtracted from this estimate.")
