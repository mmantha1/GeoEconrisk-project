import streamlit as st
from src.agents.graph import compiled_graph

st.set_page_config(layout="wide")

# Display a centered, compact version of the banner to avoid vertical scrolling
col_left, col_mid, col_right = st.columns([1.5, 1, 1.5])
with col_mid:
    st.image("assets/dashboard_banner.png", use_container_width=True)

st.title("🌐 Geo-Economic Risk Forecaster Dashboard")
st.caption("Powered by Multi-Agent LangGraph System Structures")

# Collect user constraints
target_input = st.text_input(
    "**Key Business Node, Sourcing Dependency, or Research Target to Evaluate:**", 
    placeholder="e.g., Critical Semiconductor Manufacturing Centers in Hsinchu, Taiwan",
    help="Enter a specific commodity, resource, sourcing location, or research target to analyze (e.g. 'Lithium in Chile' or 'Semiconductors in Taiwan'). The system will dynamically evaluate climate and geopolitical physical hazards and regulatory risks."
)

if st.button("Generate Diagnostic Risk Report", type="primary"):
    if not target_input.strip():
        st.warning("Please input a valid asset node location to continue.")
    else:
        with st.spinner("Orchestrating agent workflows and processing historical risk data..."):
            # Initial state inputs
            initial_state = {
                "target_node": target_input,
                "climate_analysis": None,
                "geopol_analysis": None,
                "final_synthesis": None,
                "risk_score": 0.0,
                "errors": []
            }
            
            # Execute compiled multi-agent network
            final_output = compiled_graph.invoke(initial_state)
            
            # Layout UI sections
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Calculated Fragility Index Metric", value=f"{final_output['risk_score']} / 10.0")
            
            st.subheader("📋 Executive Mitigation Strategy Summary")
            st.markdown(final_output["final_synthesis"])
            
            # Download button for the generated report
            st.download_button(
                label="📥 Download Report as TXT",
                data=final_output["final_synthesis"],
                file_name=f"risk_report_{target_input.replace(' ', '_').lower()}.txt",
                mime="text/plain"
            )
            
            with st.expander("🔍 See Underlying Agent Diagnostic Transcripts"):
                st.markdown("### Climate Stream Insights")
                st.write(final_output["climate_analysis"])
                st.markdown("### Geopolitical/Macro-Economic Stream Insights")
                st.write(final_output["geopol_analysis"])

# Subtle footer for author attribution
st.markdown("---")
st.caption("Developed by Mani Mantha")
