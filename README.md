# Swedish Municipality Explorer

**Live dashboard:** https://swedish-municipality-explorer.streamlit.app

I'm a new graduate figuring out where to settle in Sweden. I found SCB data
capturing employment, income, and education at municipality level — and
buried in it was a region of birth dimension that nobody was talking about.
As someone not born in Sweden, I couldn't ignore it. This project builds a
pipeline from raw government data to an interactive dashboard that makes
inequality visible at municipality level — for the first time.

## Features

- **Opportunity Index** — scores all 290 Swedish municipalities across four
  dimensions (Employment, Income, Education, Mobility), each normalized to a
  0–100 percentile
- **Custom weighting** — adjustable sliders and four presets (Balanced, Job
  seeker, Quality of life, Family focused) re-rank municipalities live
- **Integration lens** — filter by Population group (All residents / Born in
  Sweden / Born abroad) to surface integration gaps hidden in national
  averages
- **Interactive map** — choropleth map of the Opportunity Index across all
  290 municipalities

## Tech Stack

- **Python** — ingestion and dashboard
- **SCB PxWebApi v2** — source data (Statistics Sweden)
- **Snowflake** — RAW / STAGING / INTERMEDIATE / MARTS warehouse
- **dbt Core** — transformation pipeline
- **Streamlit** — interactive dashboard

## Architecture

```
SCB PxWebApi v2 -> Python Ingestor -> Snowflake RAW -> dbt Staging -> dbt Intermediate + Marts -> Streamlit Dashboard

  SCB PxWebApi v2          5 datasets, 2021 snapshot, 290 municipalities
  Python Ingestor          SCBClient + SnowflakeLoader — rate-limited, cell-aware chunking
  Snowflake RAW            5 raw tables, ~2,030 rows loaded
  dbt Staging              5 stg_* models — cleaned & standardized columns
  dbt Intermediate + Marts int_municipality_profiles -> dim_municipality + fct_opportunity_scores
  Streamlit Dashboard      Rankings · Compare · Map · About
```

## Data Sources (SCB PxWebApi v2)

| Dataset | SCB Table ID | What it measures | Grain |
|---|---|---|---|
| Population | BE0101A / BefolkningNy | Total population per municipality | 290 rows — 1 per municipality |
| Median income | AA0003F / IntGr5Kom | Median disposable income (price base amounts) | 290 rows — 1 per municipality |
| Employment | AM0207Z / RamsForvInt04N | Employment rate, by region of birth | 870 rows — 290 munis × 3 region-of-birth groups |
| Education | UF0506B / UtbBefRegionR | Population with post-secondary education (ISCED 5–7) | 290 rows — 1 per municipality |
| Commuting | AM0207Z / PendlingKN | Residents commuting out of the municipality for work | 290 rows — 1 per municipality |

All data is from the 2021 snapshot. Municipality code (4-digit) is the
joining key across all tables.

> **Note:** Two table paths from the original project plan returned `400 Bad
> Request` and were replaced during ingestion — Employment moved from
> `LE0105Sysselsattn02N` to `RamsForvInt04N`, and Education moved from
> `UtbSUNBefN` to `UtbBefRegionR`. See `docs/agents/agent2_ingestor.md` for
> details.

## Running Locally

```bash
git clone https://github.com/nelsonwv/swedish-municipality-explorer.git
cd swedish-municipality-explorer

# 1. Environment variables
cp .env.template .env
# fill in real Snowflake credentials in .env (never commit this file)

# 2. Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Run ingestion (SCB -> Snowflake RAW)
python ingestion/ingest_scb.py

# 4. Run dbt (RAW -> STAGING -> INTERMEDIATE -> MARTS)
cd dbt_project/swedish_municipality_explorer
dbt build
cd ../..

# 5. Run the dashboard
streamlit run dashboard/app.py
```

## Project Structure

```
swedish-municipality-explorer/
├── .env.template          # Template for Snowflake credentials (copy to .env)
├── .gitignore
├── README.md
├── requirements.txt
├── PROJECT_PLAN.md         # Data sources, data flow, agent execution order
├── docs/
│   ├── agents/             # Per-agent role, inputs, outputs, status logs
│   └── contracts/          # Data contracts for RAW/STAGING/INTERMEDIATE/MARTS
├── ingestion/              # SCB API -> Snowflake RAW ingestion (Agent 2)
├── dbt_project/            # dbt Core project (Agent 3)
├── dashboard/              # Streamlit dashboard (Agent 4)
└── presentations/          # Project presentation deck (Agent 5)
```

## Snowflake

- **Database:** `OPPORTUNITY_INDEX`
- **Schemas:** `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`
- **Warehouse:** `COMPUTE_WH`

## Links

- **Live dashboard:** https://swedish-municipality-explorer.streamlit.app
- **GitHub:** https://github.com/nelsonwv/swedish-municipality-explorer
- **LinkedIn:** linkedin.com/in/waldeannelson/

## Author

Waldean Nelson

## Status

Complete — all 5 agents shipped (scaffolding, ingestion, dbt pipeline,
dashboard, deployment & docs). See `docs/agents/` for full per-agent status
logs.
