from datetime import date, time

import pandas as pd
import streamlit as st

from config import DIFFICULTIES, PRIORITIES, WEEKDAYS
from modules.constraint_validator import validate_profile
from modules.ui import apply_style, get_profile, page_heading

apply_style()
page_heading("Student information", "Build your study profile. Subject and commitment rows can be added or removed as needed.")
profile = get_profile()
subjects = [dict(s) for s in profile.get("subjects", [])] or [{"name": "", "exam_date": None, "difficulty": "Medium", "priority": "Medium", "completed_topics": ""}]

top1, top2 = st.columns([1, 4])
with top1:
    if st.button("＋ Add subject", width="stretch"):
        subjects.append({"name": "", "exam_date": None, "difficulty": "Medium", "priority": "Medium", "completed_topics": ""})
        st.session_state["draft_subjects"] = subjects
        st.rerun()
    if len(subjects) > 1 and st.button("− Remove last", width="stretch"):
        subjects.pop()
        st.session_state["draft_subjects"] = subjects
        st.rerun()
subjects = st.session_state.pop("draft_subjects", subjects)

with st.form("student_profile_form"):
    student_name = st.text_input("Student name (optional)", value=profile.get("student_name", ""), placeholder="Your name")
    st.subheader("Subjects and examinations")
    updated_subjects = []
    for index, subject in enumerate(subjects):
        with st.expander(f"Subject {index + 1} · {subject.get('name') or 'Add details'}", expanded=index == 0):
            c1, c2, c3, c4 = st.columns([1.5, 1.2, 1, 1])
            with c1:
                subject_name = st.text_input("Subject name", value=subject.get("name", ""), key=f"subject_name_{index}")
            with c2:
                previous = subject.get("exam_date")
                if isinstance(previous, str):
                    try:
                        previous = date.fromisoformat(previous[:10])
                    except ValueError:
                        previous = None
                exam_date = st.date_input("Exam date", value=previous, key=f"exam_date_{index}")
            with c3:
                difficulty = st.selectbox("Difficulty", list(DIFFICULTIES), index=list(DIFFICULTIES).index(subject.get("difficulty", "Medium")) if subject.get("difficulty", "Medium") in DIFFICULTIES else 1, key=f"difficulty_{index}")
            with c4:
                priority = st.selectbox("Your priority", list(PRIORITIES), index=list(PRIORITIES).index(subject.get("priority", "Medium")) if subject.get("priority", "Medium") in PRIORITIES else 1, key=f"priority_{index}")
            completed = st.text_input("Completed topics (optional; separate with semicolons)", value=subject.get("completed_topics", ""), key=f"completed_{index}")
            updated_subjects.append({"name": subject_name.strip(), "exam_date": exam_date, "difficulty": difficulty, "priority": priority, "completed_topics": completed})

    st.subheader("Study availability")
    c1, c2, c3 = st.columns(3)
    with c1:
        daily_hours = st.number_input("Maximum study hours per day", min_value=0.0, max_value=24.0, value=float(profile.get("daily_hours", 0) or 0), step=0.5)
    with c2:
        start_value = profile.get("preferred_start", "09:00")
        start_time = st.time_input("Preferred start", value=time.fromisoformat(start_value) if isinstance(start_value, str) else start_value)
    with c3:
        end_value = profile.get("preferred_end", "20:00")
        end_time = st.time_input("Preferred end", value=time.fromisoformat(end_value) if isinstance(end_value, str) else end_value)
    study_days = st.multiselect("Weekly study availability", WEEKDAYS, default=[day for day in profile.get("study_days", []) if day in WEEKDAYS], help="Select the days on which study sessions may be scheduled.")
    c1, c2 = st.columns(2)
    with c1:
        session_minutes = st.number_input("Preferred session duration (minutes)", min_value=15, max_value=240, value=int(profile.get("session_minutes", 50)), step=5)
    with c2:
        break_minutes = st.number_input("Break duration (minutes)", min_value=0, max_value=60, value=int(profile.get("break_minutes", 10)), step=5)

    st.subheader("Existing commitments")
    prior = profile.get("commitments", [])
    commitment_df = pd.DataFrame([{"Day": x.get("day", "Every day"), "Start": x.get("start", "09:00"), "End": x.get("end", "10:00"), "Activity": x.get("activity", "")} for x in prior])
    if commitment_df.empty:
        commitment_df = pd.DataFrame([{"Day": "Every day", "Start": "09:00", "End": "10:00", "Activity": ""}])
    commitments_edit = st.data_editor(commitment_df, num_rows="dynamic", hide_index=True, width="stretch", column_config={"Day": st.column_config.SelectboxColumn(options=["Every day", *WEEKDAYS], required=True), "Start": st.column_config.TextColumn(help="24-hour time, for example 14:00"), "End": st.column_config.TextColumn(help="24-hour time, for example 15:00"), "Activity": st.column_config.TextColumn()})
    submitted = st.form_submit_button("Save student profile", type="primary", width="stretch")

if submitted:
    commitment_rows = []
    for item in commitments_edit.to_dict(orient="records"):
        activity = str(item.get("Activity", "")).strip()
        if activity:
            commitment_rows.append({"day": item.get("Day", "Every day"), "start": str(item.get("Start", "")).strip(), "end": str(item.get("End", "")).strip(), "activity": activity})
    new_profile = {"student_name": student_name.strip(), "subjects": updated_subjects, "daily_hours": daily_hours, "preferred_start": start_time.strftime("%H:%M"), "preferred_end": end_time.strftime("%H:%M"), "study_days": study_days, "session_minutes": int(session_minutes), "break_minutes": int(break_minutes), "commitments": commitment_rows}
    prior_profile = st.session_state.get("student_profile")
    existing_plan = st.session_state.get("timetable")
    if prior_profile is not None and prior_profile != new_profile and isinstance(existing_plan, pd.DataFrame) and not existing_plan.empty:
        st.session_state["timetable_stale"] = True
    st.session_state["student_profile"] = new_profile
    issues = validate_profile(new_profile)
    errors = [issue for issue in issues if issue["severity"] == "error"]
    st.success("Profile saved to this session.")
    if st.session_state.get("timetable_stale"):
        st.warning("Your saved timetable was created with earlier profile inputs. Regenerate it or run it through the validator again.")
    for issue in issues:
        (st.error if issue["severity"] == "error" else st.warning)(f"**{issue['check']}:** {issue['message']} {issue['suggestion']}")
    if not errors:
        st.info("Your profile is ready for subject analysis and plan generation.")
elif profile.get("subjects"):
    st.caption("Save your changes to update the profile used by the analysis and planner.")
