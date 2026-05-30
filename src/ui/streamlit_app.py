import streamlit as st
from core import CostTracker
from agents import SMEPersonaManager
from config.agent_config import AGENT_ROLES

# Initialize session state
if "cost_tracker" not in st.session_state:
    st.session_state.cost_tracker = CostTracker()

if "sme_manager" not in st.session_state:
    st.session_state.sme_manager = SMEPersonaManager(
        AGENT_ROLES["Dynamic SME Personas"],
        "claude-3-5-sonnet-20240620"
    )

# Set up the page
st.set_page_config(page_title="Multi-Agent Council", layout="wide")
st.title("Multi-Agent Council System")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Page", ["Dashboard", "Run Task", "Agent Management", "Cost Tracking"])

# Main content
if page == "Dashboard":
    st.header("Dashboard")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Agents", 15)
    with col2:
        st.metric("SME Personas", len(st.session_state.sme_manager.list_available_personas()))
    with col3:
        st.metric("Total Cost", f"${st.session_state.cost_tracker.get_total_cost():.4f}")

elif page == "Run Task":
    st.header("Run Task")
    task_input = st.text_area("Enter your task:")
    agent_selection = st.selectbox(
        "Select Agent",
        ["Orchestrator"] + list(AGENT_ROLES["Strategic Council"].keys()) + 
        list(AGENT_ROLES["Operational Agents"].keys())
    )
    
    if st.button("Run Task"):
        st.info(f"Running task: {task_input}")
        st.info(f"Using agent: {agent_selection}")
        st.success("Task completed successfully!")

elif page == "Agent Management":
    st.header("Agent Management")
    
    st.subheader("Strategic Council Agents")
    for agent_name, config in AGENT_ROLES["Strategic Council"].items():
        st.write(f"**{agent_name}**: {config['description']}")
    
    st.subheader("Operational Agents")
    for agent_name, config in AGENT_ROLES["Operational Agents"].items():
        st.write(f"**{agent_name}**: {config['description']}")
    
    st.subheader("SME Personas")
    for persona_name in st.session_state.sme_manager.list_available_personas():
        st.write(f"- {persona_name}")

elif page == "Cost Tracking":
    st.header("Cost Tracking")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Cost", f"${st.session_state.cost_tracker.get_total_cost():.4f}")
    
    with col2:
        if st.button("Reset Costs"):
            st.session_state.cost_tracker.reset()
            st.success("Costs reset successfully!")
    
    st.subheader("Cost Breakdown")
    if st.session_state.cost_tracker.costs:
        for agent_name, cost in st.session_state.cost_tracker.costs.items():
            st.write(f"**{agent_name}**: ${cost:.4f}")
    else:
        st.info("No costs recorded yet.")
