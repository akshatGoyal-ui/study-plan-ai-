import pandas as pd
import plotly.express as px
import streamlit as st

from config import APP_NAME, PROJECT_TITLE, TEAM_LEADER, TEAM_NAME
from modules.export_manager import plan_json, timetable_csv, timetable_pdf
from modules.ui import apply_style, get_profile, get_timetable, page_heading

st.set_page_config(page_title=APP_NAME, page_icon="📚", layout="wide", initial_sidebar_state="expanded")
apply_style()
profile = get_profile()
frame = get_timetable()
name = profile.get("student_name", "").strip()

page_heading("Plan with more clarity.", "A practical workspace for exam priorities, focused study sessions, and revision.")
st.markdown(f"**{PROJECT_TITLE}**  ·  {TEAM_NAME}  ·  Team lead: {TEAM_LEADER}")
st.sidebar.markdown("# 📚 StudyPlan AI")
st.sidebar.caption("Your inputs and plans stay in this Streamlit session.")

subjects = profile.get("subjects", [])
today = pd.Timestamp.today().date()
upcoming = [s for s in subjects if s.get("exam_date") and pd.notna(pd.to_datetime(s.get("exam_date"), errors="coerce")) and pd.to_datetime(s.get("exam_date"), errors="coerce").date() >= today]
planned = frame[frame.get("Session Type", pd.Series(dtype=str)).astype(str).str.casefold() != "break"] if not frame.empty else frame
planned_hours = 0.0
if not planned.empty:
    if "Duration (minutes)" in planned:
        planned_hours = pd.to_numeric(planned["Duration (minutes)"], errors="coerce").fillna(0).sum() / 60
    else:
        planned_hours = len(planned) * float(profile.get("session_minutes", 50) or 50) / 60
revision_rows = frame[frame.get("Session Type", pd.Series(dtype=str)).astype(str).isin(["Revision", "Mock Test"])] if not frame.empty else frame
revision_done = int(revision_rows.get("Completed", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not revision_rows.empty else 0
revision_total = len(revision_rows)

metrics = st.columns(4)
metrics[0].metric("Subjects", len(subjects))
metrics[1].metric("Upcoming exams", len(upcoming))
metrics[2].metric("Planned study hours", f"{planned_hours:.1f}")
metrics[3].metric("Revision progress", f"{revision_done}/{revision_total}" if revision_total else "Not started")

if not name:
    st.info("Start by adding your subjects, exam dates, availability, and commitments on the **Student Information** page.")
if st.session_state.get("timetable_stale"):
    st.warning("Your profile has changed since the current timetable was generated. Rebuild or revalidate the plan before using it.")
if not frame.empty:
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Subject-wise allocation")
        if "Subject" in planned and not planned.empty:
            allocation = planned.copy()
            allocation["Hours"] = pd.to_numeric(allocation.get("Duration (minutes)", 0), errors="coerce").fillna(0) / 60 if "Duration (minutes)" in allocation else 1
            allocation = allocation.groupby("Subject", as_index=False)["Hours"].sum()
            fig = px.bar(allocation, x="Subject", y="Hours", color="Hours", color_continuous_scale=["#a9d9dc", "#087e8b"])
            fig.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("Upcoming exams")
        exams = pd.DataFrame([{"Subject": s.get("name", ""), "Exam date": str(s.get("exam_date", "")), "Difficulty": s.get("difficulty", ""), "Priority": s.get("priority", "")} for s in upcoming])
        if not exams.empty:
            st.dataframe(exams, hide_index=True, width="stretch")
        else:
            st.caption("Exam dates appear here after you save your student information.")
    st.subheader("Daily timetable")
    display = frame.copy()
    if "Date" in display:
        display = display.sort_values(["Date", "Start Time"], kind="stable")
    st.dataframe(display, hide_index=True, width="stretch")
    st.subheader("Export your plan")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Download CSV", timetable_csv(frame), "studyplan_timetable.csv", "text/csv", width="stretch")
    c2.download_button("Download PDF", timetable_pdf(frame), "studyplan_timetable.pdf", "application/pdf", width="stretch")
    c3.download_button("Download JSON", plan_json(profile, frame), "studyplan_data.json", "application/json", width="stretch")
else:
    st.subheader("A clear path from exams to study sessions")
    cols = st.columns(3)
    cols[0].markdown("<div class='sp-card'><b>01 · Add your context</b><p class='sp-muted'>Enter subjects, exam dates, study hours, and commitments.</p></div>", unsafe_allow_html=True)
    cols[1].markdown("<div class='sp-card'><b>02 · Choose how to plan</b><p class='sp-muted'>Use the local rule-based planner, Prompt Mode, or configured API Mode.</p></div>", unsafe_allow_html=True)
    cols[2].markdown("<div class='sp-card'><b>03 · Validate and refine</b><p class='sp-muted'>Check constraints in Python, then export your plan.</p></div>", unsafe_allow_html=True)
    st.caption("No example timetable is shown as if it were your plan. Your dashboard fills from saved inputs and generated sessions.")

st.divider()
st.caption("Priority scores are calculated by a transparent Python formula. The local planner is a deterministic heuristic, not an AI response.")
