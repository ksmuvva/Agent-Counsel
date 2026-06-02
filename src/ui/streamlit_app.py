"""Streamlit web interface for the Multi-Agent Council System."""
import os
import streamlit as st

from agents.sme_personas import SMEPersonaManager
from core import CouncilSystem

st.set_page_config(page_title="Agent-Counsel", page_icon="🏛️", layout="wide")
st.title("🏛️ Agent-Counsel — Multi-Agent Council System")

with st.sidebar:
    st.header("Configuration")
    backend = st.selectbox(
        "Backend",
        ["auto", "anthropic", "glm", "offline"],
        help="'auto' tries Anthropic first, then GLM. 'glm' forces ZhipuAI GLM-4.",
    )
    if backend == "glm":
        glm_key = st.text_input("GLM API Key", type="password", value=os.getenv("GLM_API_KEY", ""))
    else:
        glm_key = os.getenv("GLM_API_KEY", "")
    budget = st.number_input("Budget (USD)", min_value=1.0, value=20.0, step=1.0)
    enforce = st.checkbox("Enforce budget", value=False)
    st.divider()
    st.subheader("Available SME Personas")
    for persona in SMEPersonaManager().list_available():
        st.caption(f"• {persona}")

task = st.text_area(
    "Task",
    value=(
        "Design a SailPoint IdentityNow implementation plan for a 5,000-employee "
        "enterprise migrating from a legacy on-premise IAM system."
    ),
    height=120,
)

if st.button("Run Council", type="primary"):
    kwargs = {"budget": budget, "enforce_budget": enforce, "backend": backend}
    if glm_key:
        kwargs["glm_api_key"] = glm_key
        if backend == "glm":
            os.environ["COUNCIL_OPUS_MODEL"] = "glm-4"
            os.environ["COUNCIL_SONNET_MODEL"] = "glm-4"
            os.environ["COUNCIL_HAIKU_MODEL"] = "glm-4"

    system = CouncilSystem(**kwargs)

    from core.runtime import Runtime
    be = Runtime.get().client.backend_name
    mode_labels = {"anthropic": "ONLINE (Claude API)", "openai": "ONLINE (GLM-4)", "offline": "OFFLINE (simulation)"}
    st.info(f"Mode: {mode_labels.get(be, be)}")

    with st.spinner("The council is deliberating..."):
        result = system.run(task)

    c1, c2, c3 = st.columns(3)
    c1.metric("Tier", result.tier)
    c2.metric("Revised", "Yes" if result.revised else "No")
    c3.metric("Passed gate", "Yes" if result.passed else "No")

    if result.selected_personas:
        st.success("Selected SME personas: " + ", ".join(result.selected_personas))

    st.subheader("Final Verdict")
    st.write(result.final_output)

    with st.expander("Phase outputs"):
        for phase, output in result.phases.items():
            st.markdown(f"**{phase}**")
            st.write(output)

    st.subheader("Cost Report")
    st.json(system.cost_summary())
