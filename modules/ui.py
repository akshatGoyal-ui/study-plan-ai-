"""Small shared Streamlit helpers."""

import pandas as pd
import streamlit as st


def apply_style() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink: #19334c; --muted: #62758a; --teal: #087e8b; --paper: #f4f7fb; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: var(--paper); }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; color: var(--ink); letter-spacing: -0.025em; }
    [data-testid="stMetric"] { background: white; border: 1px solid #e3eaf0; padding: 16px 18px; border-radius: 14px; box-shadow: 0 3px 12px rgba(25,51,76,.04); }
    .sp-eyebrow { color: var(--teal); font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .sp-muted { color: var(--muted); }
    .sp-card { background: white; border: 1px solid #e3eaf0; border-radius: 16px; padding: 20px 22px; }
    section[data-testid="stSidebar"] { background: #edf3f7; }
    div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)


def page_heading(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="sp-eyebrow">StudyPlan AI · Student productivity</div><h1>{title}</h1><p class="sp-muted">{subtitle}</p>', unsafe_allow_html=True)


def get_profile() -> dict:
    return st.session_state.get("student_profile", {"student_name": "", "subjects": [], "daily_hours": 0, "preferred_start": "09:00", "preferred_end": "18:00", "session_minutes": 50, "break_minutes": 10, "study_days": [], "commitments": []})


def get_timetable() -> pd.DataFrame:
    value = st.session_state.get("timetable")
    return value.copy() if isinstance(value, pd.DataFrame) else pd.DataFrame()


def store_timetable(frame: pd.DataFrame, source: str) -> None:
    if "Completed" not in frame.columns:
        frame = frame.copy()
        frame["Completed"] = False
    st.session_state["timetable"] = frame
    st.session_state["timetable_source"] = source
    st.session_state["timetable_stale"] = False
