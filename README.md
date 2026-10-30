# AirAware — Telugu–English Agentic AI Air Pollution Chatbot

A small course project built using Streamlit, Gemini, n8n, FastAPI, and SQLite.

## Included Data: Important

`data/delhi_pilot.csv` contains **90 synthetic demo rows** (3 Delhi stations × 30 days in January 2025). These are fictional data and must never be described as actual CPCB observations.

The data schema is CPCB-compatible, but this project does not include verified CPCB observations. Replace the demo CSV with verified daily station aggregates only after validating data provenance, units, and completeness.

Required CSV columns: `date,city,station,pm25,pm10,no2`

- Date format: `YYYY-MM-DD`
- Concentration units: µg/m³
- Missing values: blank
- For a Delhi-only pilot, use `Delhi` as the city.
- Document the completeness rule used to calculate daily averages.

## Start the Application

Install Python 3.10+ and optionally install n8n for workflow automation.

```bash
cd AirAware_Source
python -m venv .venv
```

Activate the virtual environment.

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies and configure the environment:

```bash
pip install -r requirements.txt
cp .env.example .env
```

On Windows, use:

```powershell
copy .env.example .env
```

Optionally regenerate the sample data:

```bash
python generate_sample.py
```

Start the FastAPI backend:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Open a second terminal in the same project folder, activate the virtual environment, and start Streamlit:

```bash
python -m streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser. Select **Direct API (test mode)** first.

## Enable Gemini

Obtain an API key from [Google AI Studio](https://aistudio.google.com/apikey) and place it in your local `.env` file.

Never commit `.env` or publish your API key in your presentation or repository.

Configure the Gemini model using the `GEMINI_MODEL` setting in `.env`. Without an API key, the application can use its rule-based fallback; this should not be described as an LLM-powered run.

Restart FastAPI after changing `.env`.

## n8n Workflow

Start n8n locally. One option is Docker:

```bash
docker run --rm -it --name airaware-n8n -p 5678:5678 -e N8N_SECURE_COOKIE=false n8nio/n8n
```

Use `N8N_SECURE_COOKIE=false` only for local development.

Open `http://localhost:5678` and import `workflow/airaware_n8n.json`.

The workflow is:

`Webhook → HTTP Request (/plan) → HTTP Request (/execute) → Respond to Webhook`

If n8n runs in Docker while FastAPI runs directly on your Mac or Windows computer, configure the HTTP Request node URLs to use:

- `http://host.docker.internal:8000/plan`
- `http://host.docker.internal:8000/execute`

If n8n runs directly on your computer, use `http://localhost:8000` instead.

Configure and activate the workflow before selecting **n8n automation** in Streamlit. The configured webhook endpoint is:

`http://localhost:5678/webhook/airaware-query`

For testing, n8n's test webhook may use:

`http://localhost:5678/webhook-test/airaware-query`

A test webhook is temporary and requires the workflow to be listening for a test event.

## Example Questions

- `Delhi lo PM2.5 average entha?`
- `Show daily PM10 graph`
- `Compare Anand Vihar and R K Puram PM2.5`
- `Which day had highest NO2?`
- `ఢిల్లీలో PM2.5 ఎంత ఉంది?`

Note: Exact station-pair filtering may not be implemented in the current comparison feature.

## Initial Evaluation

Evaluate the project using:

- English, Telugu, and Romanized Telugu query intent classification
- Correct pollutant extraction
- Numerical correctness against manual SQL calculations
- Successful n8n workflow executions
- Response latency

Until verified CPCB data is imported, do not report the synthetic dataset as evidence of real-world pollution conditions.

## Limitations

- Demo stations are in Delhi; multi-city comparison is not currently included.
- The application provides descriptive analytics, not an AQI calculator or forecasting model.
- Telugu responses may include a short Telugu introduction followed by an English numerical explanation.
- Gemini proposes a query plan; Python validates it and constructs safe, parameterized SQL.
- This is a local educational prototype, not a production-secured service. Do not expose unauthenticated endpoints or n8n to the public internet.