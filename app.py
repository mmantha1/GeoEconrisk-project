import uuid
import streamlit as st
from src.agents.graph import compiled_graph

st.set_page_config(layout="wide")

# Initialize Session State Variables for state-machine workflow
if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = 0

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "final_output" not in st.session_state:
    st.session_state.final_output = None

if "temp_target_input" not in st.session_state:
    st.session_state.temp_target_input = ""

if "verified" not in st.session_state:
    st.session_state.verified = False

# ==============================================================================
# WORKFLOW STEP 0: Target Input & Human Verification CAPTCHA
# ==============================================================================
if st.session_state.workflow_step == 0:
    col_img, col_title = st.columns([1, 6])
    with col_img:
        st.image("assets/dashboard_banner.png", use_container_width=True)
    with col_title:
        st.markdown("<h1 style='margin-top: 5px; margin-bottom: 0px;'>🌐 Geo-Economic Risk Forecaster</h1>", unsafe_allow_html=True)
        st.caption("Powered by Multi-Agent LangGraph Systems with Human-in-the-Loop Review")

    # Human Verification CAPTCHA widget (displayed first to verify user)
    if not st.session_state.verified:
        import random
        if "captcha_a" not in st.session_state or "captcha_b" not in st.session_state:
            st.session_state.captcha_a = random.randint(3, 15)
            st.session_state.captcha_b = random.randint(3, 15)
            st.session_state.captcha_ans = st.session_state.captcha_a + st.session_state.captcha_b
        
        with st.container(border=True):
            st.markdown("🤖 **Security Verification**")
            st.caption("Please solve the math puzzle below to verify you are a human and unlock the report generation:")
            col_c1, col_c2 = st.columns([1, 2])
            with col_c1:
                user_input = st.number_input(
                    f"What is {st.session_state.captcha_a} + {st.session_state.captcha_b}?",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=1,
                    key="captcha_input"
                )
            with col_c2:
                st.write("") # layout padding
                st.write("") # layout padding
                if st.button("Verify Identity", type="secondary"):
                    if user_input == st.session_state.captcha_ans:
                        st.session_state.verified = True
                        st.success("Verification successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect answer, please try again.")
                        # regenerate challenge
                        st.session_state.captcha_a = random.randint(3, 15)
                        st.session_state.captcha_b = random.randint(3, 15)
                        st.session_state.captcha_ans = st.session_state.captcha_a + st.session_state.captcha_b
                        st.rerun()
    else:
        # Display success and a reset button
        col_c1, col_c2 = st.columns([3, 1])
        with col_c1:
            st.success("✅ **Human Verification Completed Successfully**")
        with col_c2:
            if st.button("Reset Bot Check", type="secondary", help="Click to reset the captcha for testing purposes"):
                st.session_state.verified = False
                if "captcha_a" in st.session_state:
                    del st.session_state.captcha_a
                if "captcha_b" in st.session_state:
                    del st.session_state.captcha_b
                st.rerun()

    st.write("") # add space

    target_input = st.text_input(
        "**Key Business Node, Sourcing Dependency, or Research Target to Evaluate:**", 
        value=st.session_state.temp_target_input,
        placeholder="e.g., Critical Semiconductor Manufacturing Centers in Hsinchu, Taiwan" if st.session_state.verified else "Please complete the verification above to unlock...",
        help="Enter a specific commodity, resource, sourcing location, or research target to analyze (e.g. 'Lithium in Chile' or 'Semiconductors in Taiwan'). The system will dynamically evaluate climate and geopolitical physical hazards and regulatory risks.",
        disabled=not st.session_state.verified
    )
    st.session_state.temp_target_input = target_input

    if st.button("Generate Diagnostic Risk Report", type="primary", disabled=not st.session_state.verified):
        if not target_input.strip():
            st.warning("Please input a valid asset node location to continue.")
        else:
            # Create a fresh thread ID for checkpointer
            st.session_state.thread_id = str(uuid.uuid4())
            thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            with st.spinner("Orchestrating responsibility audit and analyst agents..."):
                # Initial state inputs
                initial_state = {
                    "target_node": target_input,
                    "climate_analysis": None,
                    "geopol_analysis": None,
                    "final_synthesis": None,
                    "risk_score": 0.0,
                    "confidence_level": None,
                    "confidence_explanation": None,
                    "errors": []
                }
                
                # Execute Phase 1: Runs Responsibility Guard, Climate Analyst, and Geopol Analyst.
                # Pauses automatically at the checkpoint before the Synthesizer node.
                output = compiled_graph.invoke(initial_state, thread_config)
                
                # Check for responsibility guard block
                if output.get("errors"):
                    st.error("⚠️ **Request Blocked by Responsibility Layer**")
                    st.markdown(output["final_synthesis"])
                else:
                    # Breakpoint reached! Move to Human-in-the-loop review step
                    st.session_state.workflow_step = 1
                    st.rerun()

    # Subtle footer for author attribution
    st.markdown("---")
    st.caption("Developed by Mani Mantha")

# ==============================================================================
# WORKFLOW STEP 1: Human-in-the-Loop Review Screen
# ==============================================================================
elif st.session_state.workflow_step == 1:
    col_img, col_title = st.columns([1, 6])
    with col_img:
        st.image("assets/dashboard_banner.png", use_container_width=True)
    with col_title:
        st.markdown("<h1 style='margin-top: 5px; margin-bottom: 0px;'>🌐 Geo-Economic Risk Forecaster</h1>", unsafe_allow_html=True)
        st.caption("Human-in-the-Loop Analyst Verification Step")

    thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
    state_info = compiled_graph.get_state(thread_config)
    
    climate_feed = state_info.values.get("climate_analysis", "")
    geopol_feed = state_info.values.get("geopol_analysis", "")
    target = state_info.values.get("target_node", "")

    st.info(
        f"🧑‍💻 **Human-in-the-Loop Review**: The analyst agents compiled findings for **'{target}'**. "
        "Review and modify their drafts below. When satisfied, click **Approve & Synthesize** to run the Synthesis Engine."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌧️ Climate & Infrastructure Draft")
        st.caption("Edit Climate Analyst findings or adjust severity tags if needed:")
        edited_climate = st.text_area("Climate Report Draft", value=climate_feed, height=450, key="edited_climate_ta")
    with col2:
        st.markdown("### ⚖️ Geopolitical & Regulatory Draft")
        st.caption("Edit Geopolitical Analyst findings or adjust severity tags if needed:")
        edited_geopol = st.text_area("Geopolitical Report Draft", value=geopol_feed, height=450, key="edited_geopol_ta")

    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if st.button("Approve & Synthesize", type="primary"):
            with st.spinner("Updating workflow checkpoint and generating executive summary..."):
                # Feed human edits back into the graph state
                compiled_graph.update_state(
                    thread_config, 
                    {
                        "climate_analysis": edited_climate, 
                        "geopol_analysis": edited_geopol
                    },
                    as_node="GeopolAnalyst"
                )
                
                # Resume execution (runs Synthesizer node using the edited states)
                final_output = compiled_graph.invoke(None, thread_config)
                
                st.session_state.final_output = final_output
                st.session_state.workflow_step = 2
                st.rerun()
    with col_btn2:
        if st.button("Cancel Analysis", type="secondary"):
            st.session_state.workflow_step = 0
            st.session_state.final_output = None
            st.rerun()

    # Subtle footer
    st.markdown("---")
    st.caption("Developed by Mani Mantha")

# ==============================================================================
# WORKFLOW STEP 2: Synthesis Results Display
# ==============================================================================
elif st.session_state.workflow_step == 2:
    col_img, col_title = st.columns([1, 6])
    with col_img:
        st.image("assets/dashboard_banner.png", use_container_width=True)
    with col_title:
        st.markdown("<h1 style='margin-top: 5px; margin-bottom: 0px;'>🌐 Geo-Economic Risk Forecaster</h1>", unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.caption("Report Synthesis Completed (Phase 2)")
    with col_t2:
        if st.button("🔄 Clear & New Query", type="secondary", key="clear_top_btn"):
            st.session_state.workflow_step = 0
            st.session_state.final_output = None
            st.session_state.temp_target_input = ""
            st.rerun()

    final_output = st.session_state.final_output
    target_input = st.session_state.temp_target_input

    if final_output:
        # Layout UI sections
        col1, col2, col3 = st.columns([1.2, 1.2, 2])
        with col1:
            st.metric(label="Calculated Fragility Index Metric", value=f"{final_output['risk_score']} / 10.0")
        with col2:
            st.metric(
                label="System Confidence Level", 
                value=final_output.get("confidence_level", "Medium"),
                help=final_output.get("confidence_explanation", "")
            )
        with col3:
            st.info(
                "**What this means:**\n"
                "The **Fragility Index (0-10)** is a weighted composite score reflecting overall risk: "
                "**40% Climate hazards** (grounded in vector DB records) and "
                "**60% Geopolitical & Regulatory risks** (computed from World Bank & Comtrade APIs). "
                "System Confidence reflects data completeness and clarity of target node context."
            )
        
        # Small card explaining the confidence reasoning below metrics
        st.caption(f"ℹ️ **Confidence Assessment:** {final_output.get('confidence_explanation', 'No detailed reasoning provided.')}")
        
        st.subheader("📋 Executive Mitigation Strategy Summary")
        st.markdown(final_output["final_synthesis"])
        
        col_down, col_restart = st.columns([1, 4])
        with col_down:
            # Download button for the generated report
            st.download_button(
                label="📥 Download Report as TXT",
                data=final_output["final_synthesis"],
                file_name=f"risk_report_{target_input.replace(' ', '_').lower()}.txt",
                mime="text/plain"
            )
        with col_restart:
            if st.button("Start New Analysis", type="secondary"):
                st.session_state.workflow_step = 0
                st.session_state.final_output = None
                st.session_state.temp_target_input = ""
                st.rerun()
        
        with st.expander("🔍 See Underlying Agent Diagnostic Transcripts (Human-Edited)"):
            st.markdown("### Climate Stream Insights")
            st.write(final_output["climate_analysis"])
            st.markdown("### Geopolitical/Macro-Economic Stream Insights")
            st.write(final_output["geopol_analysis"])

    # Subtle footer
    st.markdown("---")
    st.caption("Developed by Mani Mantha")
