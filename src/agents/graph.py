from langgraph.graph import StateGraph, END
from src.agents.state import AgenticState
from src.agents.nodes import (
    climate_analyst_node, 
    geopol_analyst_node, 
    supply_chain_synthesizer_node
)

# Initialize Workflow Graph using our Typed Dictionary State
workflow = StateGraph(AgenticState)

# Add processing step execution blocks
workflow.add_node("ClimateAnalyst", climate_analyst_node)
workflow.add_node("GeopolAnalyst", geopol_analyst_node)
workflow.add_node("Synthesizer", supply_chain_synthesizer_node)

# Construct routing flow execution paths
# Run analysis nodes sequentially to assemble all sub-agent feeds
workflow.set_entry_point("ClimateAnalyst")
workflow.add_edge("ClimateAnalyst", "GeopolAnalyst")
workflow.add_edge("GeopolAnalyst", "Synthesizer")
workflow.add_edge("Synthesizer", END)

# Compile backend architecture engine
compiled_graph = workflow.compile()
