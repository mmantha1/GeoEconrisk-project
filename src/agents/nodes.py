# src/agents/nodes.py
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.utils import load_settings
from src.agents.state import AgenticState

# Import your data engineering tools and databases
from src.tools.macro_tools import get_country_macro_metrics
from src.tools.trade_tools import get_bilateral_trade_flows
from src.database.vector_store import RiskVectorDatabase

# 1. Initialize configuration and structural classes
config = load_settings()
vdb = RiskVectorDatabase()

llm = ChatGoogleGenerativeAI(
    model=config["llm"]["model_name"], 
    temperature=config["llm"]["temperature"]
)

with open("config/prompts.yaml", "r") as f:
    PROMPTS = yaml.safe_load(f)

def extract_country_iso(prompt: str) -> str:
    """Uses Gemini to identify the primary country in the prompt and returns its 3-letter ISO code."""
    system_message = (
        "You are an expert geographical data assistant. Identify the primary country mentioned in the user's query "
        "and output ONLY its 3-letter ISO 3166-1 alpha-3 code (e.g., USA, TWN, CHL, DEU, IRN). "
        "If no country is mentioned, you are unsure, or it refers to a non-country node, output 'USA'. "
        "Do not include any other text, quotes, or markdown formatting."
    )
    try:
        response = llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content=prompt)
        ])
        iso = response.content.strip().replace('"', '').replace("'", "").upper()
        if len(iso) == 3 and iso.isalpha():
            return iso
    except Exception as e:
        print(f"Error in country ISO extraction: {e}")
    return "USA"

def responsibility_guard_node(state: AgenticState) -> dict:
    """Evaluates input query safety, injection, crash prevention, and relevance using Gemini."""
    import json
    import re
    target = state["target_node"]
    
    system_prompt = PROMPTS["responsibility_guard_prompt"]
    user_prompt = f"Target Input to Evaluate: {target}"
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        text = response.content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n", "", text)
            text = re.sub(r"\n```$", "", text)
        text = text.strip()
        
        safety_data = json.loads(text)
        is_safe = safety_data.get("is_safe", True)
        reason = safety_data.get("reason", "Safe")
    except Exception as e:
        is_safe = True
        reason = "Safe"
        text_lower = response.content.lower() if 'response' in locals() else ""
        if "false" in text_lower or '"is_safe": false' in text_lower:
            is_safe = False
            reason = "Potential safety violation or injection attempt flagged by responsibility system."
            
    if not is_safe:
        warning_msg = f"""### ⚠️ Safety Warning: Request Blocked

The request was flagged by the **Geo-Economic Risk Forecaster's Responsibility Layer**.

**Reason:** {reason}

If you believe this was in error, please rephrase your research target to refer directly to a commodity, physical asset, or geographic sourcing location (e.g. "Copper in Chile", "Semiconductor manufacturing in Oregon")."""
        return {
            "errors": [f"Safety Check Failed: {reason}"],
            "final_synthesis": warning_msg,
            "risk_score": 0.0,
            "confidence_level": "N/A",
            "confidence_explanation": "Execution blocked by responsibility guard."
        }
        
    return {"errors": []}

def climate_analyst_node(state: AgenticState) -> dict:
    """Queries vector indices for local research papers to calculate physical exposures."""
    target = state["target_node"]
    
    # Fetch real contextual data from your Qdrant Vector Store
    try:
        db_context_list = vdb.query_semantic_context(f"Climate hazards for {target}", limit=2)
        db_context = "\n".join(db_context_list) if db_context_list else "No localized document records found."
    except Exception as e:
        db_context = f"Vector DB Retrieval bypassed: {str(e)}"
    
    system_prompt = PROMPTS["climate_analyst_prompt"]
    user_prompt = f"""
    Target Node Location: {target}
    Grounding Document Context from Vector Database:
    {db_context}
    
    Analyze structural climate exposures based on this target profile.
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    return {"climate_analysis": response.content}

def geopol_analyst_node(state: AgenticState) -> dict:
    """Queries the World Bank and UN Comtrade APIs to assess systemic macro stability."""
    target = state["target_node"]
    
    # Dynamically extract country ISO code using the LLM helper
    country_iso = extract_country_iso(target)
            
    # Fetch live financial metrics and trade volumes from your API tools
    macro_data = get_country_macro_metrics(country_iso)
    trade_data = get_bilateral_trade_flows(reporter_iso=country_iso, commodity_code="TOTAL")
    
    system_prompt = PROMPTS["geopol_analyst_prompt"]
    user_prompt = f"""
    Target Asset Location Profile: {target}
    Live World Bank Country Metrics ({country_iso}): {macro_data}
    Live UN Comtrade Primary Partner Flows: {trade_data}
    
    Analyze trade friction, tariffs, and regulatory risk utilizing this data.
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    return {"geopol_analysis": response.content}

def supply_chain_synthesizer_node(state: AgenticState) -> dict:
    """Combines upstream data feeds to score composite fragility and plan routing paths."""
    import re
    
    def extract_severity_score(text: str, default: float = 5.0) -> float:
        if not text:
            return default
        match = re.search(r"<severity_score>\s*([0-9.]+)\s*</severity_score>", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return default

    def extract_tag(text: str, tag: str, default: str = "") -> str:
        if not text:
            return default
        match = re.search(fr"<{tag}>\s*(.*?)\s*</{tag}>", text, flags=re.DOTALL)
        if match:
            return match.group(1).strip()
        return default

    target = state["target_node"]
    climate_feed = state["climate_analysis"] or ""
    geopol_feed = state["geopol_analysis"] or ""
    
    # Extract scores
    climate_severity = extract_severity_score(climate_feed, default=6.5)
    geopol_severity = extract_severity_score(geopol_feed, default=7.0)
    
    # Clean the feeds to remove the tags
    clean_climate = re.sub(r"<severity_score>.*?</severity_score>", "", climate_feed, flags=re.DOTALL).strip()
    clean_geopol = re.sub(r"<severity_score>.*?</severity_score>", "", geopol_feed, flags=re.DOTALL).strip()
    
    # Fetch weight scalars from settings.yaml configuration matrix
    weights = config["risk_weight_matrix"]
    
    system_prompt = PROMPTS["synthesizer_prompt"]
    user_prompt = f"""
    Target Node: {target}
    Upstream Climate Input: {clean_climate}
    Upstream Economic Input: {clean_geopol}
    
    Synthesize alternative paths and output your strategic mitigation summary.
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    
    # Extract confidence rating & explanation
    confidence_level = extract_tag(response.content, "confidence_level", default="Medium")
    confidence_explanation = extract_tag(response.content, "confidence_explanation", default="Standard confidence based on available records.")
    
    # Clean synthesis of confidence XML tags
    clean_synthesis = re.sub(r"<confidence_level>.*?</confidence_level>", "", response.content, flags=re.DOTALL)
    clean_synthesis = re.sub(r"<confidence_explanation>.*?</confidence_explanation>", "", clean_synthesis, flags=re.DOTALL).strip()
    
    calculated_score = round(
        (climate_severity * weights["climate_physical_risk"]) + 
        (geopol_severity * (weights["regulatory_tariff_friction"] + weights["geopolitical_instability"])),
        2
    )
    
    return {
        "final_synthesis": clean_synthesis, 
        "risk_score": calculated_score,
        "climate_analysis": clean_climate,
        "geopol_analysis": clean_geopol,
        "confidence_level": confidence_level,
        "confidence_explanation": confidence_explanation
    }

