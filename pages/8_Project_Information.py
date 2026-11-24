import streamlit as st

from config import PROJECT_TITLE, TEAM_LEADER, TEAM_NAME
from modules.ui import apply_style, page_heading

apply_style()
page_heading("Project information", "A mini-project on prompt engineering, schedule constraints, and responsible AI integration.")
st.markdown(f"### {PROJECT_TITLE}\n\n**Course:** SCSE4041  \n**Team:** {TEAM_NAME}  \n**Team leader:** {TEAM_LEADER}")
st.subheader("Problem statement")
st.write("Students balance multiple subjects, exam dates, varying difficulty, and fixed commitments. StudyPlan AI organizes these inputs into an inspectable study plan and separates prompt design from deterministic validation.")
st.subheader("Architecture")
st.markdown("- **Streamlit pages** collect inputs and display analysis, prompts, plans, validation, revision, testing, and project details.\n- **Python modules** calculate transparent priorities, create a local heuristic plan, validate constraints, build prompts, parse optional AI responses, and export files.\n- **Pandas and Plotly** handle tabular data and dashboard visualizations.\n- **OpenAI API** is optional and reads credentials from Streamlit secrets, environment variables, or a session-only password field.")
st.subheader("Responsible behavior")
st.markdown("- API keys are never stored in source files.\n- Local rule-based planning is labeled separately from model output.\n- An AI response is parsed and checked in Python; a response is never assumed valid.\n- Prompt iteration observations remain pending until real outputs are reviewed.\n- Automated checks evaluate deterministic behavior; subjective model quality needs separate human review.")
st.subheader("Pages")
st.write("Home / Dashboard · Student Information · Exam & Subject Analysis · Generate Study Plan · Prompt Engineering Lab · Timetable Validator · Revision Planner · Testing & Evaluation · Project Information")
