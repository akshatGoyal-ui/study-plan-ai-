import streamlit as st

from modules.constraint_validator import validate_timetable
from modules.revision_planner import create_revision_plan
from modules.ui import apply_style, get_profile, page_heading

apply_style()
page_heading("Revision planner", "Place short recall sessions and mock tests near each exam, guided by completed topics.")
profile = get_profile()
if not profile.get("subjects"):
    st.info("Add subjects and exam dates before creating a revision plan.")
else:
    st.caption("Revision slots are proposed around the exam timeline and profile availability. Run the validator before relying on the plan.")
    if st.button("Create revision plan", type="primary"):
        plan = create_revision_plan(profile)
        if plan.empty:
            st.warning("No upcoming revision slots fit the profile. Check exam dates, study days, and available hours.")
        else:
            st.session_state["revision_plan"] = plan
    revision = st.session_state.get("revision_plan")
    if revision is not None and not revision.empty:
        st.dataframe(revision, hide_index=True, width="stretch")
        validation = validate_timetable(revision, profile)
        if validation["valid"]:
            st.success("No error-level issues were found in the revision plan.")
        else:
            st.error("The revision plan has error-level issues. Review the warnings below; it is not valid.")
        for issue in validation["issues"]:
            (st.error if issue["severity"] == "error" else st.warning)(f"**{issue['check']}:** {issue['message']} {issue['suggestion']}")
        if st.button("Use this revision plan as the dashboard timetable"):
            from modules.ui import store_timetable
            store_timetable(revision, "Revision planner")
            st.success("Revision plan saved as the current timetable.")
