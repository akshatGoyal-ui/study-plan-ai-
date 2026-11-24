import streamlit as st

from modules.ai_service import generate_with_api, parse_timetable_response, resolve_api_key
from modules.constraint_validator import validate_timetable
from modules.prompt_engine import PROMPT_FILES, build_prompt
from modules.timetable_generator import generate_local_plan
from modules.ui import apply_style, get_profile, get_timetable, page_heading, store_timetable

apply_style()
page_heading("Generate a study plan", "Choose a transparent local draft, copy/paste Prompt Mode, or direct API Mode.")
profile = get_profile()
if not profile.get("subjects"):
    st.info("Add subjects and exam dates on Student Information before generating a plan.")
else:
    mode = st.radio("Planning mode", ["Local planner (no AI)", "Prompt Mode", "API Mode"], horizontal=True)
    if mode == "Local planner (no AI)":
        st.caption("A deterministic Python heuristic schedules the submitted subjects and constraints. This is not an AI-generated result.")
        if st.button("Build local timetable", type="primary"):
            try:
                generated = generate_local_plan(profile)
                store_timetable(generated, "Local rule-based planner")
                st.success(f"Created {len(generated)} session and break rows with the local planner.")
            except (ValueError, TypeError) as exc:
                st.error(str(exc))
    elif mode == "Prompt Mode":
        version = st.selectbox("Prompt version", list(PROMPT_FILES))
        prompt = build_prompt(version, profile)
        st.markdown("#### Copy this prompt")
        st.caption("Use the copy control in the code block, paste it into ChatGPT, then paste its full response below.")
        st.code(prompt, language="text", wrap_lines=True)
        response = st.text_area("Paste the AI-generated timetable response", key="prompt_mode_response", height=240, placeholder='Paste the JSON object or Markdown timetable returned by ChatGPT.')
        if st.button("Parse pasted response", type="primary"):
            try:
                parsed = parse_timetable_response(response)
                store_timetable(parsed, f"Prompt Mode · {version}")
                st.success(f"Parsed {len(parsed)} timetable rows. The Python validator will check the constraints below.")
            except ValueError as exc:
                st.error(f"Response could not be parsed: {exc}")
    else:
        st.caption("API Mode requires an OpenAI API key. ChatGPT subscriptions do not include API usage automatically; API billing and access are separate.")
        secret_store = None
        try:
            secret_store = st.secrets
        except Exception:
            pass
        configured_key = resolve_api_key(secret_store)
        api_key = configured_key or st.text_input("OpenAI API key (used for this session only)", type="password", help="Alternatively set OPENAI_API_KEY in your environment or Streamlit secrets.")
        if configured_key:
            st.success("An API key is available from the environment or Streamlit secrets.")
        if not api_key:
            st.info("API Mode is unavailable until a key is configured. Prompt Mode and the local planner work without one.")
        if st.button("Generate with OpenAI", type="primary", disabled=not bool(api_key)):
            with st.spinner("Requesting a timetable from the configured API…"):
                try:
                    response = generate_with_api(profile, api_key)
                    parsed = parse_timetable_response(response)
                    store_timetable(parsed, "OpenAI API · V3 Optimized")
                    st.session_state["raw_ai_response"] = response
                    st.success(f"Received and parsed {len(parsed)} timetable rows. Review the Python validation results below.")
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))
        if st.session_state.get("raw_ai_response"):
            with st.expander("View raw API response"):
                st.code(st.session_state["raw_ai_response"], language="json")

frame = get_timetable()
if not frame.empty:
    st.divider()
    st.subheader("Current timetable")
    st.caption(f"Source: {st.session_state.get('timetable_source', 'Unknown')}. Mark completed revision sessions to track progress on the dashboard.")
    edited = st.data_editor(frame, key="plan_editor", hide_index=True, width="stretch", num_rows="dynamic", column_config={"Completed": st.column_config.CheckboxColumn("Completed", default=False)})
    if st.button("Save timetable edits"):
        store_timetable(edited, st.session_state.get("timetable_source", "Edited timetable"))
        st.success("Timetable edits saved for this session.")
    validation = validate_timetable(frame, profile)
    if validation["valid"]:
        st.success(f"Python validation: no error-level issues. {validation['checks_passed']}/{validation['checks_total']} checks passed.")
    else:
        st.error(f"Python validation found error-level issues. {validation['checks_passed']}/{validation['checks_total']} checks passed. This timetable is not valid.")
    for issue in validation["issues"]:
        (st.error if issue["severity"] == "error" else st.warning)(f"**{issue['check']}:** {issue['message']} {issue['suggestion']}")
