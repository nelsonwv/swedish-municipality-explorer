# Agent 4 — Dashboard

## Role

Builds the Streamlit dashboard that visualizes the Swedish Municipality
Opportunity Index, reading from the `MARTS` schema and allowing users to
filter by region of birth (All / Born in Sweden / Born abroad).

## Inputs Required Before Starting

- `docs/contracts/data_contract_marts.md`.
- Populated `MARTS` tables from Agent 3 (`dim_municipality`,
  `fct_opportunity_scores`).
- A populated `.env` file with valid Snowflake credentials.
- Python virtual environment from Agent 1 with `requirements.txt`
  installed (includes `streamlit`, `pandas`, `plotly`).

## Outputs

- Streamlit application under `dashboard/` (entry point, e.g.
  `dashboard/app.py`).
- Dashboard reads only from `OPPORTUNITY_INDEX.MARTS`
  (`dim_municipality`, `fct_opportunity_scores`).
- A region-of-birth filter (`total` / `born_in_sweden` / `born_abroad`)
  that updates the displayed Opportunity Index and component scores.
- Visualizations (e.g. map/table/charts via Plotly) showing the
  Opportunity Index and its components per municipality.
- Updated status log in this file.

## Constraints

- Do NOT write Python ingestion logic or dbt models.
- Do NOT query `RAW`, `STAGING`, or `INTERMEDIATE` schemas directly —
  only `MARTS`.
- Do NOT hardcode credentials — load all Snowflake connection details from
  environment variables via `.env`.
- Do NOT change the `MARTS` contract — if additional fields are needed,
  flag this for Agent 3 and document the request in this log.

## Status Log

<!-- Append updates below as work progresses -->
