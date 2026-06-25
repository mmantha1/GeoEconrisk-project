# src/tools/trade_tools.py
import requests
from src.utils import load_settings

config = load_settings()
BASE_URL = config["api_endpoints"]["un_comtrade"]

def get_bilateral_trade_flows(reporter_iso: str, commodity_code: str = "TOTAL", year: str = "2024") -> dict:
    """
    Fetches international trade flow volumes for a given country and commodity group.
    
    Args:
        reporter_iso (str): 3-letter ISO code of the reporting country (e.g., 'USA').
        commodity_code (str): Harmonized System (HS) commodity code (e.g., '8542' for Electronic Integrated Circuits).
        year (str): The calendar year for evaluation.
    """
    # UN Comtrade v1 public API routing schema layout
    # Default parameters pull total imports and exports for the target node
    url = f"{BASE_URL}/C/A/HS/hs/{year}/{reporter_iso}/all/{commodity_code}"
    
    # Note: Public access endpoints typically require a primary subscription key header
    headers = {
        "Ocp-Apim-Subscription-Key": "YOUR_UN_COMTRADE_KEY_IF_APPLICABLE"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", [])
            
            if not results:
                return {"status": "success", "message": f"No active records found for code {commodity_code} in {year}."}
                
            # Parse top trade interactions safely 
            parsed_flows = []
            for record in results[:5]:  # Extract the top 5 trading pairs
                parsed_flows.append({
                    "flow_direction": record.get("flowDesc"), # Import vs Export
                    "partner": record.get("partnerISO"),      # Trading partner country
                    "value_usd": record.get("primaryValue")   # Trade monetary value
                })
            return {"status": "success", "data": parsed_flows}
        else:
            return {"status": "error", "message": f"Comtrade HTTP Error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Testing UN Comtrade tracking engine tool context...")
    # 8542 corresponds universally to Electronic Integrated Circuits / Micro-assemblies
    print(get_bilateral_trade_flows(reporter_iso="USA", commodity_code="8542"))
