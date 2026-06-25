# src/tools/macro_tools.py
import requests
import pandas as pd
from src.utils import load_settings

# Load our API endpoint configuration
config = load_settings()
BASE_URL = config["api_endpoints"]["world_bank"]

def get_country_macro_metrics(country_code: str) -> dict:
    """
    Fetches key macroeconomic indicators for a specific country from the World Bank API.
    
    Args:
        country_code (str): The 3-letter ISO code of the country (e.g., 'CHL' for Chile, 'TWN' for Taiwan).
        
    Returns:
        dict: Cleaned macroeconomic metrics or an error dictionary.
    """
    # World Bank Indicator Codes:
    # NY.GDP.MKTP.CD = GDP (Current USD)
    # NE.TRD.GNFS.ZS = Trade (% of GDP)
    # FP.CPI.TOTL.ZG = Inflation, consumer prices (annual %)
    indicators = {
        "gdp": "NY.GDP.MKTP.CD",
        "trade_dependency": "NE.TRD.GNFS.ZS",
        "inflation": "FP.CPI.TOTL.ZG"
    }
    
    results = {"country_code": country_code}
    
    for metric_name, indicator_code in indicators.items():
        # Build the API URL to fetch the most recent data point
        url = f"{BASE_URL}/country/{country_code}/indicator/{indicator_code}?format=json&per_page=1"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Check if the API returned valid data points
                if len(data) > 1 and data[1] is not None and len(data[1]) > 0:
                    latest_entry = data[1][0]
                    results[metric_name] = {
                        "year": latest_entry.get("date"),
                        "value": latest_entry.get("value")
                    }
                else:
                    results[metric_name] = "No recent data available"
            else:
                results[metric_name] = f"API Error (Status {response.status_code})"
        except Exception as e:
            results[metric_name] = f"Connection Failed: {str(e)}"
            
    return results

# Quick manual test block to ensure your tool works independently
if __name__ == "__main__":
    # Test with Chile (CHL) - A major lithium exporter
    print("Testing World Bank Tool for Chile (CHL)...")
    chile_data = get_country_macro_metrics("CHL")
    print(chile_data)
