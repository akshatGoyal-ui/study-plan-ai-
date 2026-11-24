import streamlit as st

from modules.ai_service import parse_timetable_response
from modules.constraint_validator import validate_timetable
from modules.ui import apply_style, get_profile, get_timetable, page_heading, store_timetable

apply_style()
page_heading("Timetable validator", "Run real Python checks on the current schedule or parse and validate a pasted AI response.")
profile = get_profile()
current = get_timetable()
source = st.radio("Timetable source", ["Current saved timetable", "Paste a timetable response"], horizontal=True)
candidate = current
if source == "Paste a timetable response":
    pasted = st.text_area("Paste JSON or a Markdown timetable", height=220, placeholder="Paste the complete model response here.")
    if st.button("Parse and validate pasted timetable", type="primary"):
        try:
            candidate = parse_timetable_response(pasted)
            store_timetable(candidate, "Pasted response · Validator")
            st.session_state["validator_candidate"] = candidate
            st.success(f"Parsed {len(candidate)} rows; now checking the actual dates, times, commitments, and limits.")
        except ValueError as exc:
            st.error(f"Could not parse response: {exc}")
    candidate = st.session_state.get("validator_candidate", candidate)

if candidate.empty:
    st.info("No timetable is available yet. Generate a local plan or paste an AI response.")
else:
    st.dataframe(candidate, hide_index=True, width="stretch")
    result = validate_timetable(candidate, profile)
    c1, c2, c3 = st.columns(3)
    c1.metric("Checks passed", result["checks_passed"])
    c2.metric("Checks considered", result["checks_total"])
    c3.metric("Issues detected", len(result["issues"]))
    if result["valid"]:
        st.success("No error-level constraint issues were detected. Warnings may still need review.")
    else:
        st.error("This timetable has error-level issues and is not valid.")
    if result["issues"]:
        st.subheader("Warnings and suggestions")
        for issue in result["issues"]:
            (st.error if issue["severity"] == "error" else st.warning)(f"**{issue['check']}:** {issue['message']}\n\nSuggestion: {issue['suggestion']}")
    else:
        st.info("No warnings were produced by the current checks.")
    if result["daily_hours"]:
        st.subheader("Daily study load")
        st.dataframe([{"Date": d, "Study hours": hours} for d, hours in result["daily_hours"].items()], hide_index=True, width="stretch")
