from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.state import AgenticState
from src.agents.nodes import (
    responsibility_guard_node,
    climate_analyst_node, 
    geopol_analyst_node, 
    supply_chain_synthesizer_node
)

# Initialize Workflow Graph using our Typed Dictionary State
workflow = StateGraph(AgenticState)

# Add processing step execution blocks
workflow.add_node("ResponsibilityGuard", responsibility_guard_node)
workflow.add_node("ClimateAnalyst", climate_analyst_node)
workflow.add_node("GeopolAnalyst", geopol_analyst_node)
workflow.add_node("Synthesizer", supply_chain_synthesizer_node)

# Routing condition function for ResponsibilityGuard
def route_after_guard(state: AgenticState) -> str:
    if state.get("errors"):
        return END
    return "ClimateAnalyst"

# Construct routing flow execution paths
# Set entry point to ResponsibilityGuard to inspect prompts first
workflow.set_entry_point("ResponsibilityGuard")

# Route conditionally: go to ClimateAnalyst if safe, or exit to END if unsafe/invalid
workflow.add_conditional_edges(
    "ResponsibilityGuard",
    route_after_guard,
    {
        "ClimateAnalyst": "ClimateAnalyst",
        END: END
    }
)

workflow.add_edge("ClimateAnalyst", "GeopolAnalyst")
workflow.add_edge("GeopolAnalyst", "Synthesizer")
workflow.add_edge("Synthesizer", END)

# Compile backend architecture engine with memory and breakpoints
memory = MemorySaver()
compiled_graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Synthesizer"]
)
