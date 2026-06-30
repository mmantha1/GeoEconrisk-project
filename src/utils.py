# src/utils.py
import os
import yaml

# Automatically load environment variables from .env file if it exists
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip("'\"")


def load_settings(filepath="config/settings.yaml"):
    """Safely loads global system configuration parameters."""
    with open(filepath, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)
