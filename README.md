# Swedish Municipality Explorer

A data pipeline and dashboard project that builds a **Swedish Municipality
Opportunity Index** from 2021 SCB (Statistics Sweden) data, with a
Streamlit dashboard filterable by region of birth (All / Born in Sweden /
Born abroad).

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
└── dashboard/              # Streamlit dashboard (Agent 4)
```

## Data Flow

```
SCB PxWebApi v2 -> RAW -> STAGING -> INTERMEDIATE -> MARTS -> Streamlit
```

See `PROJECT_PLAN.md` for full details on data sources and the agent
pipeline, and `docs/contracts/` for the schema of each layer.

## Setup

### 1. Environment variables

```bash
cp .env.template .env
# then fill in real Snowflake credentials in .env (never commit this file)
```

### 2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. dbt

The dbt project lives in `dbt_project/`. Connection profiles are configured
via `~/.dbt/profiles.yml`, using the same environment variables as `.env`.

## Snowflake

- **Database:** `OPPORTUNITY_INDEX`
- **Schemas:** `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`
- **Warehouse:** `COMPUTE_WH`

## Status

Project scaffolding complete. See `docs/agents/agent1_pm.md` for details
and `PROJECT_PLAN.md` for the next steps (Agent 2 — Ingestion).
