"""Streamlit web interface for the Multi-Agent Council System."""
import asyncio

import streamlit as st

from agents.sme_personas import SMEPersonaManager
from core import CouncilSystem

st.set_page_config(page_title="Agent-Counsel", page_icon="🏛️", layout="wide")
st.title("🏛️ Agent-Counsel — Multi-Agent Council System")
st.caption("Real tool-using agents powered by the Claude Agent SDK.")

with st.sidebar:
    st.header("Configuration")
    budget = st.number_input("Budget (USD)", min_value=1.0, value=20.0, step=1.0)
    enforce = st.checkbox("Enforce budget", value=False)
    st.divider()
    st.subheader("Available SME Personas")
    for persona in SMEPersonaManager().list_available():
        st.caption(f"• {persona}")

task = st.text_area(
    "Task",
    value="Write a concise one-page market analysis for a new AI note-taking SaaS product.",
    height=120,
)

if st.button("Run Council", type="primary"):
    system = CouncilSystem(budget=budget, enforce_budget=enforce)
    with st.spinner("The council is deliberating (real agents)..."):
        result = asyncio.run(system.run(task))

    c1, c2 = st.columns(2)
    c1.metric("Tier", result.tier)
    c2.metric("Passed gate", "Yes" if result.passed else "No")

    if result.selected_personas:
        st.success("Selected SME personas: " + ", ".join(result.selected_personas))

    st.subheader("Final Verdict")
    st.write(result.final_output)

    with st.expander("Phase outputs"):
        for phase, output in result.phases.items():
            st.markdown(f"**{phase}**")
            st.write(output)

    st.subheader("Cost Report (real, from SDK)")
    st.json(system.cost_summary())
