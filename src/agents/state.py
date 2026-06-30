from typing import TypedDict, List, Optional, Annotated
import operator

class AgenticState(TypedDict):
    """Defines the memory dictionary shared across all multi-agent steps."""
    target_node: str               # e.g., "Semiconductors in Taiwan" or "Lithium in Chile"
    climate_analysis: Optional[str] # Documented output from the Climate Analyst
    geopol_analysis: Optional[str]  # Documented output from the Geopolitical Analyst
    final_synthesis: Optional[str]  # Combined workflow output from the Synthesizer
    risk_score: Optional[float]     # Final calculated metric (0.0 to 10.0)
    confidence_level: Optional[str] # System confidence rating (High, Medium, Low)
    confidence_explanation: Optional[str] # Explanation/reasoning for the confidence rating
    actionable_summary: Optional[str] # Crisp summary of actionable research insights
    latencies: Annotated[List[str], operator.add] # Node execution latencies
    api_statuses: Annotated[List[str], operator.add] # Live API/RAG grounding statuses
    input_tokens: Annotated[int, operator.add] # Total accumulated input tokens
    output_tokens: Annotated[int, operator.add] # Total accumulated output tokens
    hitl_impact: Optional[dict]     # Metrics representing the impact of human edits
    errors: List[str]               # Tracks processing exceptions or structural loops
