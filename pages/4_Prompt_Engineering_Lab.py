import streamlit as st

from modules.prompt_engine import PROMPT_FILES, build_prompt, compare_prompts, get_template, iteration_log
from modules.ui import apply_style, get_profile, page_heading

apply_style()
page_heading("Prompt engineering lab", "Inspect how each prompt iteration adds planning context, constraints, and output checks.")
versions = list(PROMPT_FILES)
profile = get_profile()
left, right = st.columns([1, 1])
with left:
    selected = st.selectbox("Prompt to inspect", versions)
with right:
    view = st.radio("Prompt view", ["Complete prompt", "Template only"], horizontal=True)
if view == "Complete prompt":
    st.code(build_prompt(selected, profile), language="text", wrap_lines=True)
else:
    st.code(get_template(selected), language="text", wrap_lines=True)

st.subheader("Compare versions")
c1, c2 = st.columns(2)
with c1:
    first = st.selectbox("Earlier prompt", versions, index=0, key="compare_first")
with c2:
    second = st.selectbox("Later prompt", versions, index=2, key="compare_second")
if first != second:
    st.code(compare_prompts(build_prompt(first, profile), build_prompt(second, profile)), language="diff", wrap_lines=True)
else:
    st.caption("Choose two different versions to inspect the textual changes.")

st.subheader("Iteration log")
for item in iteration_log():
    with st.expander(item["version"]):
        st.markdown(f"**Changes made:** {item['changes']}\n\n**Reason:** {item['reason']}\n\n**Expected improvement:** {item['expected']}\n\n**Actual observations:** {item['observations']}")
st.caption("Actual observations remain pending until evaluated against real model responses. No fabricated model comparison is shown.")
