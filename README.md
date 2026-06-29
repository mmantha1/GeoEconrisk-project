# Geo-Economic Risk Forecaster

An advanced research intelligence application powered by a multi-agent LangGraph system to evaluate site-specific physical climate hazards and geopolitical/macroeconomic exposures for global supply chain sourcing nodes.

---

## Key Features

1. **Multi-Agent Risk Pipeline**: Coordinates specialized agents (`ClimateAnalyst`, `GeopolAnalyst`, and `Synthesizer`) using LangGraph.
2. **Security & Responsibility Guard**: Inspects user queries at the entry point to block harmful prompts, prompt injections, and irrelevant inputs.
3. **Human-in-the-Loop (HITL) Review**: Pauses execution after the analysis phase using LangGraph's checkpointer mechanism, allowing researchers to review and edit drafts before final synthesis.
4. **Data Grounding**: Integrates semantic vector queries (Qdrant) for localized environmental data and live API feeds (World Bank and UN Comtrade) for trade/economic metrics.
5. **System Confidence Metrics**: Calculates and displays report confidence (High/Medium/Low) based on data availability.
6. **Mathematical CAPTCHA Widget**: Prevents bot-scraping and automated pipeline runs directly in the Streamlit UI.

---

## Project Structure

```text
capstone-trial/
+-- app.py                   # Main Streamlit Dashboard Application
+-- requirements.txt         # Project Dependencies
+-- verify_guard.py          # Automated safety guard rail test script
+-- verify_hitl.py           # Automated human-in-the-loop checkpoint test script
+-- config/
|   +-- prompts.yaml         # System prompts for all agents and security guards
|   \-- settings.yaml        # Weights, database, and LLM configurations
+-- src/
|   +-- utils.py             # Configuration loading utilities
|   +-- agents/
|   |   +-- graph.py         # LangGraph topology and breakpoint configuration
|   |   +-- nodes.py         # Agent execution logic and API wrappers
|   |   \-- state.py         # State TypedDict definition
|   +-- database/
|   |   +-- ingest_data.py   # Vector database ingest script
|   |   \-- vector_store.py  # Vector DB semantic query wrappers
|   +-- tools/
|       +-- macro_tools.py   # World Bank API integration
|       +-- trade_tools.py   # UN Comtrade API integration
|       \-- climate_tools.py # Climate-specific tools
```

---

## Local Setup & Installation

### 1. Prerequisites
- Python 3.10 or 3.11 installed.
- A Gemini API key (Google AI Studio).
- A Qdrant cluster host and API key (if loading custom document indices).

### 2. Environment Setup
Clone the repository and set up a Python virtual environment (e.g. using Conda):

```bash
# Create and activate environment
conda create -n geoecon_env python=3.11 -y
conda activate geoecon_env

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials
Create a `.env` file in the root of the project and add your API keys:

```ini
PYTHONPATH=.
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_HOST=https://your-qdrant-cluster-url.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
```

---

## Running the Application

### Start the Dashboard
To launch the interactive dashboard locally:

```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser to interact with the forecaster.

---

## Running Automated Tests

You can verify the security guard rails and the human-in-the-loop checkpoint process using the included test suite:

### 1. Test Safety & Guard Rails
Executes tests for safe, harmful, prompt injection, and irrelevant queries:
```bash
python verify_guard.py
```

### 2. Test Human-in-the-Loop Checkpoints
Verifies that the graph successfully pauses at the breakpoint, updates state with edits, and resumes:
```bash
python verify_hitl.py
```

---

## Cloud Deployment

### 1. Streamlit Community Cloud (Recommended)
1. Push the code to a GitHub repository.
2. Connect your repo to [Streamlit Community Cloud](https://share.streamlit.io/).
3. In the App Settings, navigate to **Secrets** and paste your API keys in TOML format:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   QDRANT_HOST = "https://your-qdrant-cluster-url.qdrant.io"
   QDRANT_API_KEY = "your_qdrant_api_key_here"
   ```

### 2. Google Cloud Run
A dockerized deploy can be built and run using GCP Buildpacks:
```bash
gcloud run deploy geoecon-risk-forecaster --source . --port 8080 --set-env-vars="GEMINI_API_KEY=...,QDRANT_HOST=...,QDRANT_API_KEY=..."
```
