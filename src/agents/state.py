from typing import TypedDict, List, Optional

class AgenticState(TypedDict):
    """Defines the memory dictionary shared across all multi-agent steps."""
    target_node: str               # e.g., "Semiconductors in Taiwan" or "Lithium in Chile"
    climate_analysis: Optional[str] # Documented output from the Climate Analyst
    geopol_analysis: Optional[str]  # Documented output from the Geopolitical Analyst
    final_synthesis: Optional[str]  # Combined workflow output from the Synthesizer
    risk_score: Optional[float]     # Final calculated metric (0.0 to 10.0)
    errors: List[str]               # Tracks processing exceptions or structural loops
