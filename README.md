# AirAware — Telugu–English Agentic AI Air Pollution Chatbot

Small-course-project starter: Streamlit + Gemini 2.5 Flash + n8n + FastAPI + SQLite.

## Included data: IMPORTANT

`data/delhi_pilot.csv` has **90 SYNTHETIC DEMO rows** (3 Delhi stations x 30 days in January 2025). These are fictional and **must never be described as CPCB observations**. The data schema is CPCB-compatible, but this project does not include your previously collected CPCB files. Replace this CSV with verified daily station aggregates and update the UI's synthetic label and `/execute` source label only after validating provenance and units.

Required CSV columns: `date,city,station,pm25,pm10,no2`; date as YYYY-MM-DD, numerical concentrations in µg/m³, missing values blank. For a Delhi-only pilot, keep city `Delhi`. Daily averages should come from valid monitored observations with a documented completeness rule.

## Start (macOS/Windows/Linux)

Install Python 3.10+ and n8n (optional for initial direct API test).

```bash
cd AirAware_Source
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                 # Windows: copy .env.example .env
python generate_sample.py            # optional: already included in the ZIP
python -m uvicorn backend.main:app --reload --port 8000
```

Open a SECOND terminal in the same folder (venv activated):

```bash
python -m streamlit run frontend/app.py
```

In Streamlit first select **Direct API (test mode)**. Browse to http://localhost:8501.

### Enable Gemini (real LLM parsing)

Put your real `GEMINI_API_KEY` into `.env`, obtained from https://aistudio.google.com/apikey. No training required. **Never paste your API key into the PPT or commit `.env`.** Restart FastAPI after changing `.env`.

Model used: `gemini-2.5-flash` via Google's official `google-genai` Python SDK. Without an API key, the app still runs with a **rule-based parsing fallback** and reports `model_used: fallback`; this is not an LLM-powered run.

### n8n workflow

Start an n8n instance, e.g. with Docker:

```bash
docker run --rm -it --name airaware-n8n -p 5678:5678 -e N8N_SECURE_COOKIE=false n8nio/n8n
```

Use the secure-cookie override only in localhost development, not on public deployments. Go to http://localhost:5678 and import `workflow/airaware_n8n.json` (menu > Import from File). The workflow is: `Webhook -> HTTP Request (Gemini /plan) -> HTTP Request (/execute) -> Respond to Webhook`.

**Important Docker networking:** If n8n is running in Docker but FastAPI runs on your host, set both HTTP Request node URLs to `http://host.docker.internal:8000/plan` and `http://host.docker.internal:8000/execute` (Mac/Windows). On Linux, provide Docker's `--add-host=host.docker.internal:host-gateway` option. If n8n runs directly on your computer, use `http://localhost:8000/...`.

Save/publish (activate) your workflow. Switch the Streamlit selector to **n8n automation**, which posts to `http://localhost:5678/webhook/airaware-query`.

For testing only, click Listen for Test Event in n8n and update `.env` to use `http://localhost:5678/webhook-test/airaware-query`; test webhook is temporary.

## Test questions

- `Delhi lo PM2.5 average entha?`
- `Show daily PM10 graph`
- `Compare Anand Vihar and R K Puram PM2.5` (comparison currently covers available stations; filtering an exact pair is not implemented)
- `Which day had highest NO2?`
- `ఢిల్లీలో PM2.5 ఎంత ఉంది?`

## Evaluation for your first review

Compare English / Telugu / Romanized Telugu query intent classification, exact pollutant extraction, numerical correctness vs manual SQL, successful n8n workflow executions, latency. Until real CPCB subset imported, do not claim real pollution findings.

## Limitations

- Demo stations are all in Delhi; no multi-city comparison yet.
- This is descriptive analytics, not an AQI calculator or forecasting model.
- Telugu responses use a short Telugu introduction plus a data-grounded English numeric explanation; full Telugu natural-language generation can be added.
- LLM only proposes a validated query plan. Safe SQL is parameterized and built by Python, not generated dynamically by Gemini.
- This is a local educational prototype, not a secured production service. Do not expose unauthenticated endpoints or n8n to the public internet.
